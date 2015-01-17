# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2014-2015 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from base64 import b64encode
from hashlib import md5
import http.client
from urllib.parse import urlencode, quote, quote_plus
import logging
import time
from threading import Timer
from . import ips
from . import namespace
from . import mapi

__all__ = ['target', 'connection', 'HcpsdkError', 'HcpsdkTimeoutError']

logging.getLogger('hcpsdk').addHandler(logging.NullHandler())


class HcpsdkError(Exception):
    # Subclasses that define an __init__ must call Exception.__init__
    # or define self.args.  Otherwise, str() will fail.
    def __init__(self, reason):
        self.args = reason,
        self.reason = reason

class HcpsdkTimeoutError(HcpsdkError):
    def __init__(self, reason):
        self.args = reason,
        self.reason = reason

class HcpsdkReplicaInitError(HcpsdkError):
    def __init__(self, reason):
        self.args = reason,
        self.reason = reason

# Interface constants
I_NATIVE = 'native'
I_HS3 = 'hs3'
I_HSWIFT = 'hswift'

# Replication strategie constants
RS_READ_ALLOWED      = 1    # allow to read from replica (always)
RS_READ_ON_FAILOVER  = 2    # automatically read from replica when failed over
RS_WRITE_ALLOWED     = 4    # allow to write to replica (always, A/A links only)
RS_WRITE_ON_FAILOVER = 8    # allow to write to replica when failed over


class target(object):
    """
    This is the a central access point to an HCP target (and its replica,
    evntually). It caches the FQDN, the port, the authentication header
    (both variants - the legacy one for HCP up to version 5 and the new
    style header for HCP version 6 and better.
    Several REST-based interface to HCP are provided (**actually, just I_NATIVE
    (the native http/REST interface) has been implemented**).
    """

    # private identifiers
    __SSL_PORTS      = [443, 8000, 9090]

    def __init__(self, fqdn, user, password, port=443, interface=I_NATIVE,
                 replica_fqdn=None, replica_strategy=None):
        """
        :param fqdn:                ([namespace.]tenant.hcp.loc)
        :param user:                HCP user name
        :param password:            the users password
        :param port:                port number
                                    (443, 8000 and 9090 are seen as ports using ssl)
        :param interface:           the HCP interface to use (I_NATIVE, I_HS3 or I_HSWIFT)
        :param replica_fqdn:        the replica HCP's FQDN
        :param replica_strategy:    or'd combination of the RS_* modes
        :raises:                    HcpsdkError
        """
        self.logger = logging.getLogger(__name__+'.target')
        self.__fqdn = fqdn
        self.__port = port
        if self.__port in target.__SSL_PORTS:
            self.__ssl = True
        else:
            self.__ssl = False
        self.interface = interface
        self.replica = None         # placeholder for a replica's *target* object
        self.replica_strategy = replica_strategy

        # instantiate an IP address circler for this target
        try:
            self.ipaddrqry = ips.Circle(self.__fqdn, port=self.__port)
        except ips.IpsError as e:
            self.logger.error(e, exc_info=True)
            raise HcpsdkError(e)

        self.logger.debug('target initialized: {}:{} - SSL = {} - IPs = {}'
                        .format(self.__fqdn, self.__port, self.__ssl, self.ipaddrqry._addresses))

        # create the authentication header(s) needed for HCP access,
        # both flavor (pre-HCP 6 and HCP 6+ are provided)
        token = b64encode(user.encode()).decode() \
            + ":" + md5(password.encode()).hexdigest()
        self.__headers = {"Authorization": 'HCP {}'.format(token),
                          "Cookie": "hcp-ns-auth={0}".format(token)}
        del(token)

        self.__headers['Host'] = self.__fqdn

        # If we have *replica_fqdn*, try to init its *target* object
        if replica_fqdn:
            try:
                self.replica = target(replica_fqdn, user, password,
                                               self.__port, interface=self.interface)
            except HcpsdkError as e:
                raise HcpsdkReplicaInitError(e)

        del(password)



    def getaddr(self):
        '''
        Convenience method to get an IP address out of the pool.

        :return:    an IP address (as string)
        '''
        return self.ipaddrqry._addr()

    # Attributes:
    def __getattr__(self, item):
        """
        Used to make .url, .ssl and .address read-only attributes
        """
        if item == 'fqdn':
            return self.__fqdn
        elif item == 'port':
            return self.__port
        elif item == 'ssl':
            return self.__ssl
        elif item == 'addresses':
            return self.ipaddrqry._addresses
        elif item == 'headers':
            return self.__headers
        elif item == 'replica':
            return self.replica
        else:
            raise AttributeError

    def __str__(self):
        return("<{} class initialized for {}>".format(target.__name__, self.__fqdn))


class connection(object):
    """
    This class represents a connection to HCP,
    caching the related parameters.
    """

    def __init__(self, target, timeout=30, idletime=30, debuglevel=0, retries=3):
        '''
        :param target:      an initialized target object
        :param timeout:     the timeout for this connection (secs)
        :param idletime:    the time the connection shall stay persistence when idle (secs)
        :param debuglevel:  0..9 -see-> http.client.HTTP[S]connetion
        :param retries:     the number of retries until giving up on a request
                            **-not yet implemented-**
        '''
        self.logger = logging.getLogger(__name__+'.connection')

        self.__target = target            # an initialized target object
        self.__address = None             # the assigned IP address to use
        self.__timeout = timeout          # the timeout for this connection (secs)
        self.__idletime = float(idletime) # the time the connection shall stay open since last usage (secs)
        self.__debuglevel = debuglevel    # 0..9 -see-> http.client.HTTP[S]connetion
        self.__retries = retries          # the number of retries until giving up on a request

        self.__con = None                 # http.client.HTTP[S]Connection object
        self._response = None

        self.__connect_time = 0.0         # record the time the connect() call took
        self.__service_time1 = 0.0        # the time a single step took (connect, 1st read, ...)
        self.__service_time2 = 0.0        # the time a request took incl. all reads, but w/o connect

        self.idletimer = None             # used to hold a threading.Timer() object

        # try:
        #     self.__con = self._connect()
        # except Exception as e:
        #     raise e
        # else:
        self.logger.log(logging.DEBUG, 'connection object initialized: IP {} ({}) - timeout: {} - idletime: {} - retries: {}'
                        .format(self.__address, self.__target.fqdn, self.__timeout, self.__idletime, self.__retries))
        # self.set_idletimer()

    def _set_idletimer(self):
        '''
        Create and start a timer
        '''
        self._cancel_idletimer()         # as a prevention, cancel a running timer
        self.idletimer = Timer(self.__idletime, self.__cancel_idletimer)
        self.idletimer.start()
        self.logger.log(logging.DEBUG, 'idletimer started: {}'.format(self.idletimer))

    def _cancel_idletimer(self):
        '''
        Cancel an active connection keep-alive timer - manually called
        '''
        if self.idletimer:
            self.idletimer.cancel()
            self.logger.log(logging.DEBUG, 'idletimer canceled: {}'.format(self.idletimer))
            self.idletimer = None
        else:
            self.logger.log(logging.DEBUG, 'tried to cancel a non-existing idletimer (pretty OK)'.format(self.idletimer))

    def __cancel_idletimer(self):
        '''
        Cancel an active connection keep-alive timer - called if timer has passed
        '''
        if self.idletimer:
            self.idletimer.cancel()
            self.logger.log(logging.DEBUG, 'idletimer timed out: {}'.format(self.idletimer))
            self.idletimer = None

    def _connect(self):
        """
        Open a new connection and return the connection object
        """
        self.__address = self.__target.getaddr()

        if self.__target.ssl:
            c_t = time.time()
            con = http.client.HTTPSConnection(self.__address, port=self.__target.port,
                                              timeout=self.__timeout)
            self.__connect_time = time.time() - c_t
        else:
            c_t = time.time()
            con = http.client.HTTPConnection(self.__address, port=self.__target.port,
                                             timeout=self.__timeout)
            self.__connect_time = time.time() - c_t
        self.logger.log(logging.DEBUG, 'connection open: IP {} ({}) - connect_time: {}'
                        .format(self.__address, self.__target.fqdn, self.__connect_time))

        if self.__debuglevel:
            con.set_debuglevel(self.__debuglevel)
        return con


    def request(self, method, url, body=None, params=None, headers=None):
        """
        Wraps the *http.client.HTTP[s]connection.request()* method to be able to
        catch any exception that might happen plus to be able to trigger
        hcpsdk.target to do a new DNS query.

        *Url* and *params* will be urlencoded, by default.

        **Beside of *method*, all arguments are valid for the convenience methods, too.**

        :param method:  any valid http method (GET,HEAD,PUT,POST,DELETE)
        :param url:     the url to access w/o the server part (i.e: /rest/path/object)
        :param body:    the payload to send (see *http.client* documentation
                        for details)
        :param params:  a dictionary with parameters to be added to the request:

                        ``{'verbose': 'true', 'retention': 'A+10y', ...}``

                        or a list of 2-tuples:

                        ``[('verbose', 'true'), ('retention', 'A+10y'), ...]``

        :param headers: a dictionary holding additional key/value pairs to add to the
                        auto-prepared header
        :return:        the original response object received from
                        *http.client.HTTP[s]connection.requests()*.
        """
        self._cancel_idletimer()                      # 1st, cancel the idletimer
        if not headers:
            headers = self.__target.headers
        else:
            headers.update(self.__target.headers)

        # make sure that the URL and params are proper encoded
        url = quote_plus(url, safe='/')
        if params:
            url = url + '?' + urlencode(params)
        self.logger.log(logging.DEBUG, 'URL = {}'.format(url))

        retry = False
        while True:
            try:
                if retry:
                    self.__con = self._connect()
                s_t = time.time()
                self.__con.request(method, url, body=body, headers=headers)
                self.__service_time1 = self.__service_time2 = time.time() - s_t
                self.logger.log(logging.DEBUG, '{} request for {} - service_time1 = {}'
                                .format(method, url, self.__service_time1))
            except (http.client.NotConnected, AttributeError) as e:
                """
                This is a trigger for the case the connection is not open
                (not yet opened or has been closed by being not used for some
                time). So, we open up a new connection and start over by calling
                our self again...
                """
                if not retry:
                    self.logger.log(logging.DEBUG, 'connection needs to be opened')
                    retry = True
                    continue
                else:
                    raise HcpsdkError('Not connected, retry failed ({})'.format(str(e)))
            except TimeoutError:
                self.logger.log(logging.DEBUG, 'connection closed after timeout')
                self.close()
                raise HcpsdkTimeoutError('Timeout - {}'.format(url))
            except http.client.HTTPException as e:
                self.logger.log(logging.DEBUG, 'request raised exception: {}'.format(str(e)))
                raise e
            except Exception as e:
                self.logger.log(logging.DEBUG, 'request raised exception: {}'.format(str(e)))
                raise HcpsdkError(str(e))
            else:
                self._response = self.__con.getresponse()

            self._set_idletimer()
            return self._response


    def getheader(self, *args, **kwargs):
        '''
        Used to get a single response header. Wraps *http.client.response.getheader()*.
        Arguments are simply passed through.
        '''
        return self._response.getheader(*args, **kwargs)


    def getheaders(self):
        '''
        Used to get a the response headers. Wraps *http.client.response.getheaders()*.
        '''
        return self._response.getheaders()


    def PUT(self, url, body=None, params=None, headers=None):
        '''
        Convenience method for request() - PUT an object.
        Cleans up and leaves the connection ready for the next request.
        For parameter description see *request()*.
        '''
        r = self.request('PUT', url, body, headers)
        r.read()                                    # clean up
        return r

    def GET(self, url, params=None, headers=None):
        """
        Convenience method for request() - GET an object.
        You need to fully *.read()* the requested content from the connection before
        it can be used for another request.
        For parameter description see *request()*.
        """
        return self.request('GET', url, params=params, headers=headers)

    def HEAD(self, url, params=None, headers=None):
        """
        Convenience method for request() - HEAD - get metadata of an object.
        Cleans up and leaves the connection ready for the next request.
        For parameter description see *request()*.
        """
        r = self.request('HEAD', url, params=params, headers=headers)
        r.read()                                    # clean up
        return r


    def POST(self, url, params=None, headers=None):
        """
        Convenience method for request() - POST metadata.
        Cleans up and leaves the connection ready for the next request.
        For parameter description see *request()*.
        """
        r = self.request('POST', url, params=params, headers=headers)
        r.read()                                    # clean up
        return r


    def DELETE(self, url, params=None, headers=None):
        """
        Convenience method for request() - DELETE an object.
        Cleans up and leaves the connection ready for the next request.
        For parameter description see *request()*.
        """
        r = self.request('DELETE', url, params=params, headers=headers)
        r.read()                                    # clean up
        return r


    def read(self, amt=None):
        '''
        Read amt # of bytes (or all, if amt isn't given) from a response.

        :param amt: number of bytes to read
        :return:    the requested number of bytes; fewer (or zero) bytes signal
                    end of transfer, which means that the connection is ready
                    for another request.
        '''
        s_t = time.time()
        buf = self._response.read(amt)
        self.__service_time1 = time.time() - s_t
        self.logger.log(logging.DEBUG, '(partial?) read: service_time1 = {} secs'
                        .format(self.__service_time1))
        self.__service_time2 += self.__service_time1
        return buf


    def __getattr__(self, item):
        """
        Used to make .address read-only attributes
        """
        if item == 'address':
            return self.__address
        if item == 'con':
            return self.__con
        if item == 'response':
            return self._response
        if item == 'response_status':
            return None or self._response.status
        if item == 'response_reason':
            return None or self._response.reason
        if item == 'connect_time':
            if self.__connect_time > 0.0:
                return self.__connect_time
            else:
                return 0.00000000001
        if item == 'service_time1':
            if self.__service_time1 > 0.0:
                return self.__service_time1
            else:
                return 0.00000000001
        if item == 'service_time2':
            if self.__service_time2 > 0.0:
                return self.__service_time2
            else:
                return 0.00000000001
        else:
            raise AttributeError

    def close(self):
        '''
        Close the connection. **It is essential to close the connection**,
        as open connections might keep the program from terminating for at
        max *timeout* seconds, due to the fact that the timer used to keep
        the connection persistent runs in a separate thread, which will
        be canceled on *close()*.
        '''
        try:
            self._cancel_idletimer()
            self.__con.close()
        except:
            pass
        self.logger.log(logging.DEBUG, 'connection object closed: IP {} ({})'
                        .format(self.__address, self.__target.fqdn))

    def __str__(self):
        return("<{} class initialized for fqdn {} @ {}>".format(connection.__name__,
                                                                self.__target.authority,
                                                                self.__address))

