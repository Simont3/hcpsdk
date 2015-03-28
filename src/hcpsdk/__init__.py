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
# As of Python 3.4.3, http.client.HTTPSconnection() will default to verify
# presented certificates against the system's trusted CA chain. To enable
# the previous behaviour, we switch it off.
import ssl
try:
    SSL_NOVERIFY = ssl._create_unverified_context()
except (AttributeError, NameError):
    SSL_NOVERIFY = None
import socket
import http.client
from urllib.parse import urlencode, quote
import logging
import time
from threading import Timer

# noinspection PyProtectedMember
from .version import _Version
from . import ips
from . import namespace
from . import mapi
from . import pathbuilder


__all__ = ['Target', 'Connection', 'BaseAuthorization', 'DummyAuthorization',
           'NativeAuthorization', 'HcpsdkError', 'HcpsdkCantConnectError',
           'HcpsdkTimeoutError', 'HcpsdkCertificateError', 'HcpsdkReplicaInitError']

logging.getLogger('hcpsdk').addHandler(logging.NullHandler())

version = _Version()


class HcpsdkError(Exception):
    """
    Subclasses that define an __init__ must call Exception.__init__
    or define self.args.  Otherwise, str() will fail.
    """
    def __init__(self, reason):
        self.args = reason,
        self.reason = reason


class HcpsdkCantConnectError(HcpsdkError):
    """
    Raised if we can't connect to the HCP node
    """
    def __init__(self, reason):
        self.args = reason,
        self.reason = reason


class HcpsdkTimeoutError(HcpsdkError):
    """
    Raised if we have a timeout
    """
    def __init__(self, reason):
        self.args = reason,
        self.reason = reason


class HcpsdkCertificateError(HcpsdkError):
    """
    Raised if we can't verify against the presented ssl certificate
    """
    def __init__(self, reason):
        self.args = reason,
        self.reason = reason


class HcpsdkReplicaInitError(HcpsdkError):
    """
    Raised if we can't setup the internal *Target* for the replica HCP
    """
    def __init__(self, reason):
        self.args = reason,
        self.reason = reason

# Interface constants
I_DUMMY = 'I_DUMMY'
I_NATIVE = 'I_NATIVE'
I_HS3 = 'I_HS3'
I_HSWIFT = 'I_HSWIFT'

# Replication strategie constants
RS_READ_ALLOWED = 1  # allow to read from replica (always)
RS_READ_ON_FAILOVER = 2  # automatically read from replica when failed over
RS_WRITE_ALLOWED = 4  # allow to write to replica (always, A/A links only)
RS_WRITE_ON_FAILOVER = 8  # allow to write to replica when failed over

# The ports used for https
SSL_PORTS = [443, 8000, 9090]


class BaseAuthorization(object):
    """
    Represents the authorization for a *Target*.

    This is a base class for all other *Authorization* classes, not intended for
    direct usage, but to be sub-classed for specific protocols.
    """
    def __init__(self):
        """
        Calculate or acquire the authorization token (or whatever needed) to build the
        required authorization header(s).
        """
        self.logger = logging.getLogger(__name__ + '__name__')
        self.headers = {}   # the headers that authorize a request

    def _createauthorization(self):
        """
        Do whatever is needed to create the authorization token.

        This method needs to be overwritten to suite the needs of a specific
        protocol.

        :return:    a dict holding the necessary headers
        """

    def _refreshauthorization(self):
        """
        Do whatever is needed to refresh the authorization token.
        This method will be called by *Target* if an refresh of the authorization
        header(s) is required.

        This method needs to be overwritten if the specific protocol to refresh
        its authorization token from time to time.

        :return:    a dict holding the necessary headers
        :raises:    HcpsdkError
        """
        pass

    def _getheaders(self):
        """
        This method will be called by *Target* to get the authorization header(s).

        :returns:   a dict holding the authorization headers
        :raises:    HcpsdkError, if no credentials are available
        """
        if self.headers:
            return self.headers
        else:
            raise HcpsdkError('Err: no authorization token available')


class DummyAuthorization(BaseAuthorization):
    """
    Dummy authorization for the :term:`Default Namespace <Default Namespace>`.
    """
    def __init__(self):
        super().__init__()
        self.headers = {'HCPSDK_DUMMY': 'DUMMY'}
        self.logger.debug('*I_DUMMY* dummy authorization initialized')


class NativeAuthorization(BaseAuthorization):
    """
    Authorization for native http/REST access to HCP.
    """
    def __init__(self, user, password):
        """
        :param user:        the data access user
        :param password:    his password
        """
        super().__init__()
        self.headers = self._createauthorization(user, password)
        self.logger.debug('*I_NATIVE* authorization initialized for user: {}'
                          .format(user))
        self.logger.debug('pre version 6:     Cookie: {}'.format(self.headers['Cookie']))
        self.logger.debug('version 6+: Authorization: {}'.format(self.headers['Authorization']))

    def _createauthorization(self, user, password):
        """
        Build the authorization headers by calculation from user and password.

        :param user:        the name of a local HCP user
        :param password:    his password
        :return:            a dict holding the necessary headers
        """
        token = b64encode(user.encode()).decode() + ":" + md5(password.encode()).hexdigest()
        return {"Authorization": 'HCP {}'.format(token),
                "Cookie": "hcp-ns-auth={0}".format(token)}


class Target(object):
    """
    This is the a central access point to an HCP target (and its replica,
    eventually). It caches the FQDN and the port and queries the provided
    *Authorization* object for the required authorization token.
    """

    def __init__(self, fqdn, authorization, port=443, dnscache=False, sslcontext=SSL_NOVERIFY,
                 interface=I_NATIVE, replica_fqdn=None, replica_strategy=None):
        """
        :param fqdn:                ([namespace.]tenant.hcp.loc)
        :param authorization:       an instance of one of BaseAuthorization's subclasses
        :param port:                port number (443, 8000 and 9090 are seen as ports
                                    using ssl)
        :param dnscache:            if True, use the system resolver (which **might** do
                                    local caching), else use an internal resolver,
                                    bypassing any cache available
        :param sslcontext:          the context used to handle https requests; defaults to
                                    no certificate verification
        :param interface:           the HCP interface to use (I_NATIVE)
        :param replica_fqdn:        the replica HCP's FQDN (not yet implemented)
        :param replica_strategy:    ORed combination of the RS_* modes
        :raises:                    *ips.IpsError* if DNS query fails, *HcpsdkError* in all
                                    other fault cases
        """
        self.logger = logging.getLogger(__name__ + '.Target')
        self.__fqdn = fqdn
        self.__authorization = authorization
        self.__dnscache = dnscache
        self.__sslcontext = sslcontext
        self.__headers = {'Host': self.__fqdn}
        self.__port = port
        if self.__port in SSL_PORTS:
            self.__ssl = True
        else:
            self.__ssl = False
        self.interface = interface
        self.replica = None  # placeholder for a replica's *Target* object
        self.replica_strategy = replica_strategy

        # instantiate an IP address circler for this Target
        try:
            self.ipaddrqry = ips.Circle(self.__fqdn, port=self.__port, dnscache=self.__dnscache)
        except ips.IpsError as e:
            self.logger.debug(e, exc_info=True)
            raise ips.IpsError(e)
        except Exception as e:
            raise HcpsdkError(e)

        # noinspection PyProtectedMember
        self.logger.debug('Target initialized: {}:{} - SSL = {}'
                          .format(self.__fqdn, self.__port, self.__ssl))

        # If we have *replica_fqdn*, try to init its *Target* object
        if replica_fqdn:
            # try:
            #     self.replica = Target(replica_fqdn, user, password,
            #                           self.__port, interface=self.interface)
            # except HcpsdkError as e:
            #     raise HcpsdkReplicaInitError(e)
            raise HcpsdkReplicaInitError('Error: not yet implemented')

    def getaddr(self):
        """
        Convenience method to get an IP address out of the pool.

        :return:    an IP address (as string)
        """
        # noinspection PyProtectedMember
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
        elif item == 'sslcontext':
            return self.__sslcontext
        elif item == 'addresses':
            # noinspection PyProtectedMember
            return self.ipaddrqry._addresses
        elif item == 'headers':
            tmp = self.__headers.copy()
            tmp.update(self.__authorization._getheaders())
            return tmp
        elif item == 'replica':
            return self.replica
        else:
            raise AttributeError

    def __str__(self):
        return "<{} class initialized for {}>".format(Target.__name__, self.__fqdn)


class Connection(object):
    """
    This class represents a Connection to HCP,
    caching the related parameters.
    """

    # noinspection PyShadowingNames
    def __init__(self, target, timeout=30, idletime=30, retries=0, debuglevel=0):
        """
        :param target:      an initialized Target object
        :param timeout:     the timeout for this Connection (secs)
        :param idletime:    the time the Connection shall stay persistence when idle (secs)
        :param retries:     the number of retries until giving up on a Request
        :param debuglevel:  0..9 -see-> `http.client.HTTPconnection <https://docs.python.org/3/library/http.client.html?highlight=http.client#http.client.HTTPConnection.set_debuglevel>`_

        *Connection()* retries *request()s* if:
            a)  the underlying connection has been closed by HCP before *idletime* has passed
                (the request will be retried using the existing connection context) or
            b)  a timeout emerges during an active request, in which case the connection
                is closed, *Target()* is urged to refresh its cache of IP addresses, a fresh
                IP address is acquired from the cache and the connection is setup from scratch.
        """
        self.logger = logging.getLogger(__name__ + '.Connection')

        # This is here to allow test cases to inject error situations.
        # You need to set _fail to an exception object...
        self._fail = None
        #################

        self.__target = target  # an initialized Target object
        self.__address = None  # the assigned IP address to use
        self.__timeout = timeout  # the timeout for this Connection (secs)
        self.__idletime = float(idletime)  # the time the Connection shall stay open since last usage (secs)
        self.__debuglevel = debuglevel  # 0..9 -see-> http.client.HTTP[S]connetion
        self.__retries = retries  # the number of retries until giving up on a Request

        self.__sslcontext = self.__target.sslcontext
        self.__con = None  # http.client.HTTP[S]Connection object
        self._response = None

        self.__connect_time = 0.0  # record the time the connect() call took
        self.__service_time1 = 0.0  # the time a single step took (connect, 1st read, ...)
        self.__service_time2 = 0.0  # the time a Request took incl. all reads, but w/o connect

        self.idletimer = None  # used to hold a threading.Timer() object

        self.logger.log(logging.DEBUG,
                        'Connection object initialized: IP {} ({}) - timeout: {} - idletime: {} - retries: {}'
                        .format(self.__address, self.__target.fqdn, self.__timeout, self.__idletime, self.__retries))
        if self.__sslcontext:
            self.logger.log(logging.DEBUG, 'SSLcontext = {}'.format(self.__sslcontext))

    def _set_idletimer(self):
        """
        Create and start a timer
        """
        self._cancel_idletimer()  # as a prevention, cancel a running timer
        self.idletimer = Timer(self.__idletime, self.__cancel_idletimer)
        self.idletimer.start()
        self.logger.log(logging.DEBUG, 'idletimer started: {}'.format(self.idletimer))

    def _cancel_idletimer(self):
        """
        Cancel an active Connection keep-alive timer - manually called
        """
        if self.idletimer:
            self.idletimer.cancel()
            self.logger.log(logging.DEBUG, 'idletimer canceled: {}'.format(self.idletimer))
            self.idletimer = None
        else:
            self.logger.log(logging.DEBUG,
                            'tried to cancel a non-existing idletimer (pretty OK)'.format(self.idletimer))

    def __cancel_idletimer(self):
        """
        Cancel an active Connection keep-alive timer - called if timer has passed
        """
        if self.idletimer:
            self.idletimer.cancel()
            self.logger.log(logging.DEBUG, 'idletimer timed out: {}'.format(self.idletimer))
            self.idletimer = None

    def _connect(self):
        """
        Open a new Connection and return the Connection object
        """
        self.__address = self.__target.getaddr()

        if self.__target.ssl:
            c_t = time.time()
            con = http.client.HTTPSConnection(self.__address, port=self.__target.port,
                                              timeout=self.__timeout, context=self.__sslcontext)
            self.__connect_time = time.time() - c_t
        else:
            c_t = time.time()
            con = http.client.HTTPConnection(self.__address, port=self.__target.port,
                                             timeout=self.__timeout)
            self.__connect_time = time.time() - c_t
        self.logger.log(logging.DEBUG, 'Connection open: IP {} ({}) - connect_time: {}'
                        .format(self.__address, self.__target.fqdn, self.__connect_time))

        if self.__debuglevel:
            con.set_debuglevel(self.__debuglevel)
        return con

    def request(self, method, url, body=None, params=None, headers=None):
        """
        Wraps the *http.client.HTTP[s]Connection.Request()* method to be able to
        catch any exception that might happen plus to be able to trigger
        hcpsdk.Target to do a new DNS query.

        *Url* and *params* will be urlencoded, by default.

        **Beside of *method*, all arguments are valid for the convenience methods, too.**

        :param method:  any valid http method (GET,HEAD,PUT,POST,DELETE)
        :param url:     the url to access w/o the server part (i.e: /rest/path/object)
        :param body:    the payload to send (see *http.client* documentation
                        for details)
        :param params:  a dictionary with parameters to be added to the Request:

                        ``{'verbose': 'true', 'retention': 'A+10y', ...}``

                        or a list of 2-tuples:

                        ``[('verbose', 'true'), ('retention', 'A+10y'), ...]``

        :param headers: a dictionary holding additional key/value pairs to add to the
                        auto-prepared header
        :return:        the original *Response* object received from
                        *http.client.HTTP[s]Connection.requests()*.
        :raises:        one of the *hcpsdk.Hcpsdk[..]Error*\ s or
                        *hcpsdk.ips.IpsError* in case an IP address cache refresh failed
        """
        self._cancel_idletimer()  # 1st, cancel the idletimer
        if not headers:
            headers = self.__target.headers
        else:
            headers.update(self.__target.headers)

        # make sure that the URL and params are proper encoded
        url = quote(url, safe='/')
        if params:
            url = url + '?' + urlencode(params, safe='+')
        self.logger.log(logging.DEBUG, 'URL = {}'.format(url))

        initialretry = False    # used if connection isn't open
        retryonfailure = False  # used for retries on failures
        retries = 0             # - " -
        while True:
            try:
                if retryonfailure:
                    retryonfailure = False
                    self.close()
                    self.__target.ipaddrqry.refresh()
                    self.__con = self._connect()
                if initialretry:
                    self.close()
                    self.__con = self._connect()
                    initialretry = False

                # This is to allow a test case to inject an error situation...
                if self._fail:
                    __e = self._fail
                    self._fail = None
                    raise __e('test case')
                ####################

                self.logger.log(logging.DEBUG, '{} About to request for {}'
                                .format(method, url))
                s_t = time.time()
                self.__con.request(method, url, body=body, headers=headers)
            except ips.IpsError as e:
                """
                This is a trigger for the case that *hcpsdk.ips* isn't able to
                resolve IP addresses - we simple forward it, as we can't resolve.
                """
                self._fail = None
                raise
            except (http.client.NotConnected, AttributeError) as e:
                """
                This is a trigger for the case the Connection is not open
                (not yet opened or has been closed by being not used for some
                time). So, we open up a new Connection and start over by calling
                our self again...
                """
                self._fail = None
                if not initialretry:
                    self.logger.log(logging.DEBUG, 'Connection needs to be opened')
                    initialretry = True
                    continue
                else:
                    self.close()
                    raise HcpsdkError('Can\'t connect, retry failed ({})'
                                      .format(str(e)))
            except ConnectionAbortedError as e:
                """
                This is a trigger for the case that HCP aborts a connection for
                whatever reason. It also serves to catch WinError 10053 on Windows,
                which stands for a close caused by the OS.
                We close the connection, force the target to refresh its address list
                and retry with a new connection.
                """
                self._fail = None
                self.logger.debug('ConnectionAbortedError: {} Request for {} failed ({})'
                                  .format(method, url, e))
                if retries < self.__retries:
                    retries += 1
                    retryonfailure = True
                    self.logger.log(logging.DEBUG, 'ConnectionAbortedError - retry # {}'.format(retries))
                    continue
                else:
                    self.logger.log(logging.DEBUG, 'ConnectionAbortedError ({} retries), giving up'
                                    .format(retries))
                    self.close()
                    raise HcpsdkTimeoutError('ConnectionAbortedError (giving up after {} retries) - {}'.format(retries, url))
            except http.client.CannotSendRequest as e:
                """
                If this gets raised, the underlying connection seems to be in a state where
                it can't handle a new request, yet.
                We'll try it with the same approach as with the ConnectionAbortedError...
                """
                self._fail = None
                self.logger.exception('http.client.CannotSendRequest: {} Request for {} failed (retry)'
                                      .format(method, url))
                initialretry = True
                continue
            except http.client.ResponseNotReady as e:
                """
                If this gets raised, the underlying connection seems to be in a state where
                it can't handle a new request, yet.
                We'll try it with the same approach as with the ConnectionAbortedError...
                """
                self._fail = None
                self.logger.debug('http.client.ResponseNotReady: {} Request for {} failed ({})'
                                  .format(method, url, e))
                if retries < self.__retries:
                    retries += 1
                    retryonfailure = True
                    self.logger.log(logging.DEBUG, 'http.client.ResponseNotReady - retry # {}'.format(retries))
                    continue
                else:
                    self.logger.log(logging.DEBUG, 'http.client.ResponseNotReady ({} retries), giving up'
                                    .format(retries))
                    self.close()
                    raise HcpsdkTimeoutError('http.client.ResponseNotReady (giving up after {} retries) - {}'
                                             .format(retries, url))

            except ssl.SSLError as e:
                """
                This is a blocking issue - will *not* retry and will close the
                underlying connection.
                """
                self._fail = None
                self.logger.log(logging.DEBUG, 'ssl.SSLError: {}'.format(str(e)))
                self.close()
                raise HcpsdkCertificateError(str(e))
            except (TimeoutError, socket.timeout) as e:
                """
                We will retry in this case (if retries have been asked for). If we fail
                we close the underlying connection.
                """
                self._fail = None
                self.logger.debug('TimeoutError: {} Request for {} failed ({})'
                                  .format(method, url, e))
                if retries < self.__retries:
                    retries += 1
                    retryonfailure = True
                    self.logger.log(logging.DEBUG, 'TimeoutError - retry # {}'.format(retries))
                    continue
                else:
                    self.logger.log(logging.DEBUG, 'TimeoutError ({} retries), giving up'
                                    .format(retries))
                    self.close()
                    raise HcpsdkTimeoutError('Timeout ({} retries) - {}'.format(retries, url))
            except http.client.HTTPException as e:
                """
                Again, there might be no recovery from this, so we close the underlying
                connection and give up.
                """
                self._fail = None
                self.logger.exception('unexpected HTTPException')
                self.close()
                raise HcpsdkError(str(e))
            except Exception as e:
                """
                Again, there might be no recovery from this, so we close the underlying
                connection and give up.
                """
                self._fail = None
                self.logger.exception('unexpected Exception')
                self.close()
                raise HcpsdkError(str(e))
            else:
                self.__service_time1 = self.__service_time2 = time.time() - s_t
                self.logger.log(logging.DEBUG, '{} Request for {} - service_time1 = {}'
                                .format(method, url, self.__service_time1))

                try:
                    self._response = self.__con.getresponse()
                except (TimeoutError, socket.timeout) as e:
                    if retries < self.__retries:
                        retries += 1
                        self.logger.log(logging.DEBUG, 'TimeoutError while getting response - retry # {}'
                                        .format(retries))
                        continue
                    else:
                        self.logger.log(logging.DEBUG, 'TimeoutError while getting response ({} retries), giving up'
                                        .format(retries))
                        self.close()
                        raise HcpsdkTimeoutError('Timeout ({} retries) - {}'.format(retries, url))
                except http.client.BadStatusLine as e:
                    # BadStatusLine most likely means that HCP has closed the connection.
                    # ('HTTP Persistent Connection Timeout Interval' < Connection.timeout)
                    # So, we close the connection here and trigger a retry...
                    self.close()
                    if retries < self.__retries:
                        retries += 1
                        retryonfailure = True
                        self.logger.log(logging.DEBUG,
                                        'HCP most likely closed the connection - retry # {}'
                                        .format(retries))
                        continue
                    else:
                        self.logger.log(logging.DEBUG,
                                        'HCP most likely closed the connection ({} retries, giving up)'
                                        .format(retries))
                        raise HcpsdkTimeoutError('HCP most likely closed the connection ({} retries) - {}'
                                                 .format(retries, url))
                except Exception as e:
                    self.logger.exception(str(e))

            self._set_idletimer()
            return self._response

    def getheader(self, *args, **kwargs):
        """
        Used to get a single *Response* header. Wraps *http.client.Response.getheader()*.
        Arguments are simply passed through.
        """
        return self._response.getheader(*args, **kwargs)

    def getheaders(self):
        """
        Used to get a the *Response* headers. Wraps *http.client.Response.getheaders()*.
        """
        return self._response.getheaders()

    # noinspection PyUnusedLocal,PyPep8Naming
    def PUT(self, url, body=None, params=None, headers=None):
        """
        Convenience method for Request() - PUT an object.
        Cleans up and leaves the Connection ready for the next Request.
        For parameter description see *Request()*.
        """
        r = self.request('PUT', url, body, params, headers)
        r.read()  # clean up
        return r

    # noinspection PyPep8Naming
    def GET(self, url, params=None, headers=None):
        """
        Convenience method for Request() - GET an object.
        You need to fully *.read()* the requested content from the Connection before
        it can be used for another Request.
        For parameter description see *Request()*.
        """
        return self.request('GET', url, params=params, headers=headers)

    def HEAD(self, url, params=None, headers=None):
        """
        Convenience method for Request() - HEAD - get metadata of an object.
        Cleans up and leaves the Connection ready for the next Request.
        For parameter description see *Request()*.
        """
        r = self.request('HEAD', url, params=params, headers=headers)
        r.read()  # clean up
        return r

    def POST(self, url, body=None, params=None, headers=None):
        """
        Convenience method for Request() - POST metadata.
        Does no clean-up, as a POST can have a response body!
        For parameter description see *Request()*.
        """
        r = self.request('POST', url, body=body, params=params, headers=headers)
        return r

    def DELETE(self, url, params=None, headers=None):
        """
        Convenience method for Request() - DELETE an object.
        Cleans up and leaves the Connection ready for the next Request.
        For parameter description see *Request()*.
        """
        r = self.request('DELETE', url, params=params, headers=headers)
        r.read()  # clean up
        return r

    def read(self, amt=None):
        """
        Read amt # of bytes (or all, if amt isn't given) from a *Response*.

        :param amt: number of bytes to read
        :return:    the requested number of bytes; fewer (or zero) bytes signal
                    end of transfer, which means that the Connection is ready
                    for another Request.
        """
        s_t = time.time()
        try:
            buf = self._response.read(amt)
            self.__service_time1 = time.time() - s_t
        except AttributeError as e:
            msg = 'faulty read: {}'.format(str(e))
            self.logger.log(logging.DEBUG, msg)
            raise HcpsdkError(msg)
        except (http.client.IncompleteRead, OSError) as e:
            msg = 'read error: {}'.format(str(e))
            self.logger.log(logging.DEBUG, msg)
            raise HcpsdkError(msg)
        else:
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
        if item == 'Response':
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
        """
        Close the Connection. **It is essential to close the Connection**,
        as open connections might keep the program from terminating for at
        max *timeout* seconds, due to the fact that the timer used to keep
        the Connection persistent runs in a separate thread, which will
        be canceled on *close()*.
        """
        # noinspection PyBroadException
        if self.__con:
            try:
                self._cancel_idletimer()
                self.__con.close()
            except Exception as e:
                self.logger.exception('Connection object close failed: IP {} ({})'
                                .format(self.__address, self.__target.fqdn))

        self.logger.log(logging.DEBUG, 'Connection object closed: IP {} ({})'
                        .format(self.__address, self.__target.fqdn))

    def __str__(self):
        return ("<{} class initialized for fqdn {} @ {}>".format(Connection.__name__,
                                                                 self.__target.fqdn,
                                                                 self.__address))

