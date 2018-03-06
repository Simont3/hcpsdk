# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2014-2017 Thorsten Simons (sw@snomis.de)
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

import sys
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

# If we install using pip, we run into an error if we don't have
# dnspython installed; that's why we accept the ImportError here.
try:
    from . import ips
except ImportError as e:
    print('ImportError: {} - install dnspython >= 1.15.0'.format(e),
          file=sys.stderr)

from . import httpclient
from . import namespace
from . import mapi
from . import pathbuilder


__all__ = ['Target', 'Connection', 'BaseAuthorization', 'DummyAuthorization',
           'NativeAuthorization', 'NativeADAuthorization',
           'LocalSwiftAuthorization', 'HcpsdkError',
           'HcpsdkCantConnectError', 'HcpsdkTimeoutError',
           'HcpsdkCertificateError', 'HcpsdkReplicaInitError']

logging.getLogger('hcpsdk').addHandler(logging.NullHandler())

version = _Version()

RFC3986_reserved_chars = ':?#[]@!$&\'()*+,;='

class HcpsdkError(Exception):
    """
    Raised on generic errors in **hcpsdk**.
    """
    def __init__(self, reason):
        """
        :param reason:  an error description
        """
        self.args = (reason,)


class HcpsdkCantConnectError(HcpsdkError):
    """
    Raised if a connection couldn't be established.
    """
    def __init__(self, reason):
        """
        :param reason:  an error description
        """
        self.args = (reason,)


class HcpsdkTimeoutError(HcpsdkError):
    """
    Raised if a Connection timed out.
    """
    def __init__(self, reason):
        """
        :param reason:  an error description
        """
        self.args = (reason,)


class HcpsdkCertificateError(HcpsdkError):
    """
    Raised if the *SSL context* doesn't verify a certificate
    presented by HCP.
    """
    def __init__(self, reason):
        """
        :param reason:  an error description
        """
        self.args = (reason,)


class HcpsdkReplicaInitError(HcpsdkError):
    """
    Raised if the setup of the internal *Target* for the replica HCP failed
    (typically, this is a name resolution problem). **If
    this exception is raised, the primary Target's init failed, too.**
    You'll need to retry!
    """
    def __init__(self, reason):
        """
        :param reason:  an error description
        """
        self.args = (reason,)


class HcpsdkPortError(HcpsdkError):
    """
    Raised if the Target is initialized with an invalid port.
    """
    def __init__(self, reason):
        """
        :param reason:  an error description
        """
        self.args = (reason,)

# Port constants
P_HTTP = 80
P_HTTPS = 443
P_MGMT = 8000
P_SEARCH = 8888
P_MAPI = 9090


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
        self.headers = {}   # the headers that authorize a request

    def _createauthorization(self):
        """
        Do whatever is needed to create the authorization token.

        This method needs to be overwritten to suite the needs of a specific
        protocol.

        :return:    a dict holding the necessary headers
        """
        return self.headers

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
        return self.headers

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
        self.logger = logging.getLogger(__name__ + '.DummyAuthorization')
        self.headers = {'HCPSDK_DUMMY': 'DUMMY'}
        self.logger.debug('*I_DUMMY* dummy authorization initialized')

    def __repr__(self):
        return ('{}()'.format(__class__.__name__))

    def __str__(self):
        return ('{}'.format(__class__.__name__))


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
        self.logger = logging.getLogger(__name__ + '.NativeAuthorization')
        self.user = user
        self.headers = self._createauthorization(user, password)
        self.logger.debug('*I_NATIVE* authorization initialized for user: {}'
                          .format(user))
        self.logger.debug(
            'pre version 6:     Cookie: {}'.format(self.headers['Cookie']))
        self.logger.debug('version 6+: Authorization: {}'.format(
            self.headers['Authorization']))

    def _createauthorization(self, user, password):
        """
        Build the authorization headers by calculation from user and password.

        :param user:        the name of a local HCP user
        :param password:    his password
        :return:            a dict holding the necessary headers
        """
        token = b64encode(user.encode()).decode() + ":" + md5(
            password.encode()).hexdigest()
        return {"Authorization": 'HCP {}'.format(token),
                "Cookie": "hcp-ns-auth={0}".format(token)}

    def __repr__(self):
        return ('{}({}, {})'
                .format(__class__.__name__, self.user, 6*'*'))

    def __str__(self):
        return ('{} for user {}, password {})'
                .format(__class__.__name__, self.user, 6*'*'))


class NativeADAuthorization(BaseAuthorization):
    """
    Authorization for native http/REST access to HCP using an Active Directory
    user.

    Supported with HCP 7.2.0 and later. The user needs to be a member of the
    Active Directory domain in which HCP is joined.
    """
    def __init__(self, user, password):
        """
        :param user:        an Active Directory user
        :param password:    his password
        """
        super().__init__()
        self.logger = logging.getLogger(__name__ + '.NativeADAuthorization')
        self.headers = self._createauthorization(user, password)
        self.logger.debug('version 7.2+: Authorization: {}'.format(
            self.headers['Authorization']))

    def _createauthorization(self, user, password):
        """
        Build the authorization headers by calculation from user and password.

        :param user:        the name of a local HCP user
        :param password:    his password
        :return:            a dict holding the necessary headers
        """
        return {"Authorization": 'AD {}:{}'.format(user, password)}


    def __repr__(self):
        return ('{}({}, {})'
                .format(__class__.__name__, self.user, 6 * '*'))

    def __str__(self):
        return ('{} for user {}, password {})'
                .format(__class__.__name__, self.user, 6*'*'))


class LocalSwiftAuthorization(BaseAuthorization):
    """
    Authorization for local :term:`HSwift <HSwift>` access to
    HCP (w/o Keystone).
    """
    def __init__(self, user, password):
        """
        :param user:        the data access user
        :param password:    his password
        """
        super().__init__()
        self.logger = logging.getLogger(__name__ + '.LocalSwiftAuthorization')
        self.headers = self._createauthorization(user, password)
        self.logger.debug('Local HSwift: X-Auth-Token: {}'.format(
            self.headers['X-Auth-Token']))

    def _createauthorization(self, user, password):
        """
        Build the authorization headers by calculation from user and password.

        :param user:        the name of a local HCP user
        :param password:    his password
        :return:            a dict holding the necessary headers
        """
        token = b64encode(user.encode()).decode() + ":" + md5(
            password.encode()).hexdigest()
        return {"X-Auth-Token": "HCP {}".format(token)}

    def __repr__(self):
        return ('{}({}, {})'
                .format(__class__.__name__, self.user, 6*'*'))

    def __str__(self):
        return ('{} for user {}, password {})'
                .format(__class__.__name__, self.user, 6*'*'))


class Target(object):
    """
    This is the a central access point to an HCP target (and its replica,
    eventually). It caches the FQDN and the port and queries the provided
    *Authorization* object for the required authorization token.
    """

    def __init__(self, fqdn, authorization, port=443, dnscache=False,
                 sslcontext=SSL_NOVERIFY, interface=I_NATIVE,
                 replica_fqdn=None, replica_strategy=None):
        """
        :param fqdn:                ([namespace.]tenant.hcp.loc)
        :param authorization:       an instance of one of BaseAuthorization's subclasses
        :param port:                one of the port constants (*hcpsdk.P_**)
        :param dnscache:            if True, use the system resolver (which **might** do
                                    local caching), else use an internal resolver,
                                    bypassing any cache available
        :param sslcontext:          the context used to handle https requests; defaults to
                                    no certificate verification
        :param interface:           the HCP interface to use (I_NATIVE)
        :param replica_fqdn:        the replica HCP's FQDN
        :param replica_strategy:    OR'ed combination of the RS_* modes
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
        self.__ssl = self.__port in SSL_PORTS

        self.__interface = interface
        self.__replica = None  # placeholder for a replica's *Target* object
        self.__replica_strategy = replica_strategy

        # instantiate an IP address circler for this Target
        try:
            self.ipaddrqry = ips.Circle(self.__fqdn, port=self.__port,
                                        dnscache=self.__dnscache)
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
            #     self.__replica = Target(replica_fqdn, user, password,
            #                           self.__port, interface=self.__interface)
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

    # properties for the read-only attributes
    def __getfqdn(self):
        return self.__fqdn
    fqdn = property(__getfqdn, None, None,
                    'The FQDN for which this object was initialized (r/o)')

    def __getinterface(self):
        return self.__interface
    interface = property(__getinterface, None, None,
                         'The HCP interface used (r/o)')

    def __getport(self):
        return self.__port
    port = property(__getport, None, None,
                    'The target port in use (r/o)')

    def __getssl(self):
        return self.__ssl
    ssl = property(__getssl, None, None,
                    'Indicates if SSL is used (r/o)')

    def __getsslcontext(self):
        return self.__sslcontext
    sslcontext = property(__getsslcontext, None, None,
                    'The assigned SSL context (r/o)')

    def __getaddresses(self):
        return self.ipaddrqry._addresses
    addresses = property(__getaddresses, None, None,
                    'The list of resolved IP addresses for this target (r/o)')

    def __getheaders(self):
        tmp = self.__headers.copy()
        tmp.update(self.__authorization._getheaders())
        return tmp
    headers = property(__getheaders, None, None,
                    'The calculated authorization headers (r/o)')

    def __getreplica(self):
        return self.__replica
    replica = property(__getreplica, None, None,
                    'The target object for the HCP replica, if set (r/o)')

    def __getreplica_strategy(self):
        return self.__replica_strategy
    replica_strategy = property(__getreplica_strategy, None, None,
                    'The replica strategy selected (r/o)')

    def __repr__(self):
        return('{}({}, {}, port={}, dnscache={}, sslcontext={}, interface={}, '
               'replica_fqdn={}, replica_strategy={})'
               .format(__class__.__name__, self.__fqdn, repr(self.__authorization), self.__port,
                       self.__dnscache, repr(self.sslcontext),
                       self.__interface, self.__replica,
                       self.__replica_strategy))

    def __str__(self):
        return "{} initialized for {}".format(__class__.__name__, self.__fqdn)


class Connection(object):
    """
    This class represents a Connection to HCP,
    caching the related parameters.
    """

    # noinspection PyShadowingNames
    def __init__(self, target, timeout=30, idletime=30, retries=0,
                 debuglevel=0, sock_keepalive=False,
                 tcp_keepalive=60, tcp_keepintvl=60, tcp_keepcnt=3):
        """
        :param target:          an initialized Target object
        :param timeout:         the timeout for this Connection (secs)
        :param idletime:        the time the Connection shall stay persistence
                                when idle (secs)
        :param retries:         the number of retries until giving up on a
                                Request
        :param debuglevel:      0..9 -see->
                                `http.client.HTTPconnection <https://docs.python.org/3/library/http.client.html?highlight=http.client#http.client.HTTPConnection.set_debuglevel>`_
        :param sock_keepalive:  enable TCP keepalive, if True
        :param tcp_keepalive:   idle time used when SO_KEEPALIVE is enable
        :param tcp_keepintvl:   interval between keepalives
        :param tcp_keepcnt:     number of keepalives before close

        *Connection()* retries *request()s* if:
            a)  the underlying connection has been closed by HCP before
                *idletime* has passed (the request will be retried using the
                existing connection context) or
            b)  a timeout emerges during an active request, in which case the
                connection is closed, *Target()* is urged to refresh its cache
                of IP addresses, a fresh IP address is acquired from the cache
                and the connection is setup from scratch.

        You should rarely need this, but if you have a device in the data path
        that limits the time an idle connection can be open, this might be of
        help:

            Setting *sock_keepalive* to *True* enables TCP keep-alive for
            this connection. *tcp_keepalive* defines the idle time before a
            keep-alive packet is first sent, *tcp_keepintvl* is the time between
            keep-alive packets and *tcp_keepcnt* is the number of keep-alive
            packets to be sent before failing the connection in case the remote
            end doesn't answer.  See ``man tcp`` for the details.

            ..  versionadded:: 0.9.4.3
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
        self.sock_keepalive = sock_keepalive
        self.tcp_keepalive = tcp_keepalive
        self.tcp_keepintvl = tcp_keepintvl
        self.tcp_keepcnt = tcp_keepcnt

        self.__sslcontext = self.__target.sslcontext
        self.__con = None  # http.client.HTTP[S]Connection object
        self._response = None

        self.__connect_time = 0.0  # record the time the connect() call took
        self.__service_time1 = 0.0  # the time a single step took (connect, 1st read, ...)
        self.__service_time2 = 0.0  # the time a Request took incl. all reads, but w/o connect

        self.idletimer = None  # used to hold a threading.Timer() object

        self.logger.log(logging.DEBUG,
                        'Connection object initialized: IP {} ({}) - timeout: '
                        '{} - idletime: {} - retries: {}'
                        .format(self.__address, self.__target.fqdn,
                                self.__timeout, self.__idletime,
                                self.__retries))
        if self.__sslcontext:
            self.logger.log(logging.DEBUG,
                            'SSLcontext = {}'.format(self.__sslcontext))

    def _set_idletimer(self):
        """
        Create and start a timer
        """
        self._cancel_idletimer()  # as a prevention, cancel a running timer
        self.idletimer = Timer(self.__idletime, self.__cancel_idletimer)
        self.idletimer.start()
        # self.logger.log(logging.DEBUG, 'idletimer started: {}'.format(self.idletimer))

    def _cancel_idletimer(self):
        """
        Cancel an active Connection keep-alive timer - manually called
        """
        if self.idletimer:
            self.idletimer.cancel()
            # self.logger.log(logging.DEBUG, 'idletimer canceled: {}'.format(self.idletimer))
            self.idletimer = None
        # else:
        #     self.logger.log(logging.DEBUG,
        #                     'tried to cancel a non-existing idletimer (pretty OK)'.format(self.idletimer))

    def __cancel_idletimer(self):
        """
        Cancel an active Connection keep-alive timer - auto-called if timer
        has passed
        """
        if self.idletimer:
            self.idletimer.cancel()
            self.close()
            self.logger.log(logging.DEBUG,
                            'idletimer timed out: {}'.format(self.idletimer))
            self.idletimer = None

    def _connect(self):
        """
        Open a new Connection and return the Connection object
        """
        self.__address = self.__target.getaddr()

        if self.__target.ssl:
            c_t = time.time()
            con = httpclient.HTTPSConnection(self.__address,
                                             port=self.__target.port,
                                             timeout=self.__timeout,
                                             context=self.__sslcontext,
                                             sock_keepalive=self.sock_keepalive,
                                             tcp_keepalive=self.tcp_keepalive,
                                             tcp_keepintvl=self.tcp_keepintvl,
                                             tcp_keepcnt=self.tcp_keepcnt)
            self.__connect_time = time.time() - c_t
        else:
            c_t = time.time()
            con = httpclient.HTTPConnection(self.__address,
                                            port=self.__target.port,
                                            timeout=self.__timeout,
                                            sock_keepalive=self.sock_keepalive,
                                            tcp_keepalive=self.tcp_keepalive,
                                            tcp_keepintvl=self.tcp_keepintvl,
                                            tcp_keepcnt=self.tcp_keepcnt)
            self.__connect_time = time.time() - c_t
        self.logger.log(logging.DEBUG,
                        'Connection open: IP {} ({}) - connect_time: {:0.17f}'
                        .format(self.__address, self.__target.fqdn,
                                self.__connect_time))

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
        :param url:     the url to access w/o the server part (i.e: /rest/path/object);
                        url quoting will be done if necessary, but existing quoting
                        will not be touched
        :param body:    the payload to send (see *http.client* documentation
                        for details)
        :param params:  a dictionary with parameters to be added to the Request:

                        ``{'verbose': 'true', 'retention': 'A+10y', ...}``

                        or a list of 2-tuples:

                        ``[('verbose', 'true'), ('retention', 'A+10y'), ...]``

        :param headers: a dictionary holding additional key/value pairs to add to the
                        auto-prepared header
        :return:        the original *Response* object received from
                        *http.client.HTTP[S]Connection.requests()*.
        :raises:        one of the *hcpsdk.Hcpsdk[..]Error*\ s or
                        *hcpsdk.ips.IpsError* in case an IP address cache refresh failed
        """
        self._cancel_idletimer()  # 1st, cancel the idletimer
        if not headers:
            headers = self.__target.headers
        else:
            headers.update(self.__target.headers)

        # if url needs url-encoding, do so...
        try:
            # --> if url can be encoded to ascii and it doesn't contain
            #     forbidden characters, we can go with it.
            url.encode("ascii")
            if any([x in url for x in RFC3986_reserved_chars]):
                raise HcpsdkError('')
        except HcpsdkError:
            # in this case, we need to urlencode it...
            self.logger.log(logging.DEBUG, 'url ({}) does need quoting'.format(url))
            url = quote(url)
            self.logger.log(logging.DEBUG, 'quote(url) = {}'.format(url))
        else:
            self.logger.log(logging.DEBUG, 'url ({}) doesn\'t need quoting'.format(url))

        if params:
            url = url + '?' + urlencode(params)
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

                self.logger.log(logging.DEBUG, '{}: About to request for {}'
                                .format(method, url))
                s_t = time.time()
                self.__con.request(method, url, body=body, headers=headers)
            except ips.IpsError as e:
                # This is a trigger for the case that *hcpsdk.ips* isn't able
                # to resolve IP addresses - we simple forward it, as we can't
                # resolve.
                self._fail = None
                raise
            except ConnectionRefusedError as e:
                # This is a trigger for the case that we were able to get an
                # IP address, but a connection to it was actively refused.
                self.close()
                raise HcpsdkError('Unable to connect ({})'
                                  .format(str(e)))
            except (http.client.NotConnected, AttributeError) as e:
                # This is a trigger for the case the Connection is not open
                # (not yet opened or has been closed by being not used for some
                # time). So, we open up a new Connection and start over by
                # calling our self again...
                self._fail = None
                if not initialretry:
                    self.logger.log(logging.DEBUG,
                                    'Connection needs to be opened')
                    initialretry = True
                    continue
                else:
                    self.close()
                    raise HcpsdkError('Can\'t connect, retry failed ({})'
                                      .format(str(e)))
            except ConnectionAbortedError as e:
                # This is a trigger for the case that HCP aborts a connection
                # for whatever reason. It also serves to catch WinError 10053
                # on Windows, which stands for a close caused by the OS. We
                # close the connection, force the target to refresh its address
                # list and retry with a new connection.
                self._fail = None
                self.logger.debug(
                    'ConnectionAbortedError: {} Request for {} failed ({})'
                    .format(method, url, e))
                if retries < self.__retries:
                    retries += 1
                    retryonfailure = True
                    self.logger.log(logging.DEBUG,
                                    'ConnectionAbortedError - retry # {}'
                                    .format(retries))
                    continue
                else:
                    self.logger.log(logging.DEBUG,
                                    'ConnectionAbortedError ({} retries), '
                                    'giving up'.format(retries))
                    self.close()
                    raise HcpsdkTimeoutError(
                        'ConnectionAbortedError (giving up after {} retries) '
                        '- {}'.format(retries, url))
            except http.client.CannotSendRequest as e:
                # If this gets raised, the underlying connection seems to be in
                # a state where it can't handle a new request, yet. We'll try
                # it with the same approach as with the ConnectionAbortedError
                self._fail = None
                self.logger.log(logging.DEBUG,
                                'CannotSendRequest: {} Request for {} failed '
                                '({})'.format(method, url, e))
                if retries < self.__retries:
                    retries += 1
                    initialretry = True
                    self.logger.log(logging.DEBUG,
                                    'CannotSendRequest - retry # {}'.format(
                                        retries))
                    continue
                else:
                    self.logger.log(logging.DEBUG,
                                    'CannotSendRequest ({} retries), giving up'
                                    .format(retries))
                    self.close()
                    raise HcpsdkTimeoutError(
                        'CannotSendRequest (giving up after {} retries) - {}'
                            .format(retries, url))
            except http.client.ResponseNotReady as e:
                # If this gets raised, the underlying connection seems to be in
                # a state where it can't handle a new request, yet. We'll try it
                # with the same approach as with the ConnectionAbortedError...
                self._fail = None
                self.logger.debug(
                    'http.client.ResponseNotReady: {} Request for {} failed '
                    '({})'.format(method, url, e))
                if retries < self.__retries:
                    retries += 1
                    retryonfailure = True
                    self.logger.log(logging.DEBUG,
                                    'http.client.ResponseNotReady - retry # {}'
                                    .format(retries))
                    continue
                else:
                    self.logger.log(logging.DEBUG,
                                    'http.client.ResponseNotReady ({} retries)'
                                    ', giving up'.format(retries))
                    self.close()
                    raise HcpsdkTimeoutError(
                        'http.client.ResponseNotReady (giving up after {} '
                        'retries) - {}'.format(retries, url))

            except ssl.SSLError as e:
                # This is a blocking issue - will *not* retry and will close
                # the underlying connection.
                self._fail = None
                self.logger.log(logging.DEBUG, 'ssl.SSLError: {}'
                                .format(str(e)))
                self.close()
                raise HcpsdkCertificateError(str(e))
            except (TimeoutError, socket.timeout, BrokenPipeError) as e:
                # We will retry in this case (if retries have been asked for).
                # If we fail we close the underlying connection.
                self._fail = None
                self.logger.debug('TimeoutError: {} Request for {} failed ({})'
                                  .format(method, url, e))
                if retries < self.__retries:
                    retries += 1
                    retryonfailure = True
                    self.logger.log(logging.DEBUG, 'TimeoutError - retry # {}'
                                    .format(retries))
                    continue
                else:
                    self.logger.log(logging.DEBUG, 'TimeoutError ({} retries),'
                                                   ' giving up'
                                    .format(retries))
                    self.close()
                    raise HcpsdkTimeoutError('Timeout ({} retries) - {}'
                                             .format(retries, url))
            except http.client.HTTPException as e:
                # Again, there might be no recovery from this, so we close the
                # underlying connection and give up.
                self._fail = None
                self.logger.exception('unexpected HTTPException')
                self.close()
                raise HcpsdkError(str(e))
            except Exception as e:
                # Again, there might be no recovery from this, so we close the
                # underlying connection and give up.
                self._fail = None
                self.logger.exception('unexpected Exception')
                self.close()
                raise HcpsdkError(str(e))
            else:
                self.__service_time1 = self.__service_time2 = time.time() - s_t
                self.logger.log(logging.DEBUG,
                                '{} Request for {} - service_time1&2 = '
                                '{:0.17f}'
                                .format(method, url, self.__service_time1))

                try:
                    self._response = self.__con.getresponse()
                except (TimeoutError, socket.timeout, BrokenPipeError) as e:
                    if retries < self.__retries:
                        retries += 1
                        self.logger.log(logging.DEBUG,
                                        'TimeoutError while getting response '
                                        '- retry # {}'.format(retries))
                        continue
                    else:
                        self.logger.log(logging.DEBUG,
                                        'TimeoutError while getting response '
                                        '({} retries), giving up'
                                        .format(retries))
                        self.close()
                        raise HcpsdkTimeoutError(
                            'Timeout ({} retries) - {}'.format(retries, url))
                except (OSError, http.client.BadStatusLine) as e:
                    # BadStatusLine most likely means that HCP has closed the connection.
                    # Same for OSError 9
                    # ('HTTP Persistent Connection Timeout Interval' < Connection.timeout)
                    # So, we close the connection here and trigger a retry...
                    self.close()
                    if retries < self.__retries:
                        retries += 1
                        retryonfailure = True
                        self.logger.log(logging.DEBUG,
                                        'HCP most likely closed the connection'
                                        ' ({}) - retry # {}'
                                        .format(str(e), retries))
                        continue
                    else:
                        self.logger.log(logging.DEBUG,
                                        'HCP most likely closed the connection'
                                        ' ({} - {} retries, giving up)'
                                        .format(str(e), retries))
                        raise HcpsdkTimeoutError(
                            'HCP most likely closed the connection ({} - {} '
                            'retries) - {}'
                            .format(str(e), retries, url))
                except http.client.ResponseNotReady as e:
                    # If this gets raised, the underlying connection seems to
                    # be in a state where it can't handle a new request, yet.
                    # We'll try it with the same approach as with the
                    # ConnectionAbortedError...
                    self._fail = None
                    self.logger.debug(
                        'http.client.ResponseNotReady: {} getresponse() for '
                        '{} failed ({})'.format(method, url, e))
                    if retries < self.__retries:
                        retries += 1
                        retryonfailure = True
                        self.logger.log(logging.DEBUG,
                                        'http.client.ResponseNotReady - retry '
                                        '# {}'.format(retries))
                        continue
                    else:
                        self.logger.log(logging.DEBUG,
                                        'http.client.ResponseNotReady ({} '
                                        'retries), giving up'
                                        .format(retries))
                        self.close()
                        raise HcpsdkTimeoutError(
                            'http.client.ResponseNotReady (giving up after {}'
                            ' retries) - {}'
                            .format(retries, url))
                except Exception as e:
                    self.logger.exception(
                        'Exception not catched in hcpsdk.__init__: {}'.format(
                            str(e)))
                else:
                    self.__service_time2 = time.time() - s_t
                    self.logger.log(logging.DEBUG,
                                    '{} Request for {} - after getResponse(): '
                                    'service_time2 = {:0.17f}'
                                    .format(method, url, self.__service_time2))

            self._set_idletimer()
            return self._response

    def getheader(self, *args, **kwargs):
        """
        Used to get a single *Response* header. Wraps
        *http.client.Response.getheader()*. Arguments are simply passed
        through.
        """
        return self._response.getheader(*args, **kwargs)

    def getheaders(self):
        """
        Used to get a the *Response* headers. Wraps
        *http.client.Response.getheaders()*.
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
        You need to fully *.read()* the requested content from the Connection
        before it can be used for another Request.
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
        r.read()
        return r

    def POST(self, url, body=None, params=None, headers=None):
        """
        Convenience method for Request() - POST metadata.
        Does no clean-up, as a POST can have a response body!
        For parameter description see *Request()*.
        """
        return self.request('POST', url, body=body, params=params,
                            headers=headers)

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
        :raises:    *HcpsdkTimeoutError* in case a socket.timeout was catched,
                    *HcpsdkError* in all other cases.
        """
        s_t = time.time()
        try:
            buf = self._response.read(amt)
            self.__service_time1 = time.time() - s_t
        except AttributeError as e:
            msg = 'faulty read: {}'.format(str(e))
            self.logger.log(logging.DEBUG, msg)
            raise HcpsdkError(msg)
        except socket.timeout as e:
            msg = 'read: {}'.format(str(e))
            self.logger.log(logging.DEBUG, msg)
            raise HcpsdkTimeoutError(msg)
        except (http.client.IncompleteRead, OSError) as e:
            msg = 'read error: {}'.format(str(e))
            self.logger.log(logging.DEBUG, msg)
            raise HcpsdkError(msg)
        else:
            self.__service_time2 += self.__service_time1
            readsize = len(buf)
            if readsize:
                self.logger.log(logging.DEBUG,
                                '(partial?) read {} bytes: service_time1/2 = '
                                '{:0.17f}/{:0.17f} secs'
                                .format(readsize, self.__service_time1,
                                        self.__service_time2))
            else:
                self.logger.log(logging.DEBUG,
                                'final read: service_time1/2 = {:0.17f}/'
                                '{:0.17f} secs'
                                .format(self.__service_time1,
                                        self.__service_time2))
            return buf

    def close(self):
        """
        Close the Connection.

        .. Warning::
           **It is essential to close the Connection**, as open connections
           might keep the program from terminating for at max *timeout*
           seconds, due to the fact that the timer used to keep the Connection
           persistent runs in a separate thread, which will be canceled on
           *close()*.
        """
        # noinspection PyBroadException
        if self.__con:
            try:
                self._cancel_idletimer()
                self.__con.close()
                self.__con = None
                self.logger.log(logging.DEBUG,
                                'Connection object closed: IP {} ({})'
                                .format(self.__address, self.__target.fqdn))
            except Exception as e:
                self.logger.exception('Connection object close failed: '
                                      'IP {} ({})'
                                .format(self.__address, self.__target.fqdn))

    # properties for externally visible attributes
    def __getaddress(self):
        return self.__address
    address = property(__getaddress, None, None,
                    'The IP address for which this object was initialized '
                    '(r/o)')

    def __getcon(self):
        return self.__con
    con = property(__getcon, None, None,
                    'The internal connection object (r/o)')

    def __getresponse(self):
        return self._response
    Response = property(__getresponse, None, None,
                        '.. deprecated:: 0.9.4.2\n\n'
                        '   Use **response** instead!')
    response = property(__getresponse, None, None,
                        'Exposition of the http.client.Response object for '
                        'the last Request (r/o)\n\n'
                        '.. versionadded:: 0.9.4.2')


    def __getresponse_status(self):
        return self._response.status
    response_status = property(__getresponse_status, None, None,
                               'The HTTP status code of the last Request '
                               '(r/o)')

    def __getresponse_reason(self):
        return self._response.reason
    response_reason = property(__getresponse_reason, None, None,
                               'The corresponding HTTP status message (r/o)')

    def __getconnect_time(self):
        if self.__connect_time > 0.0:
            return self.__connect_time
        else:
            return 0.00000000001
    connect_time = property(__getconnect_time, None, None,
                            'The time in seconds the last connect took (r/o)')

    def __getservice_time1(self):
        if self.__service_time1 > 0.0:
            return self.__service_time1
        else:
            return 0.00000000001
    service_time1 = property(__getservice_time1, None, None,
                             'The time in seconds the last action on a Request'
                             ' took. This can be the initial part of PUT/GET/'
                             'etc., or a single (possibly incomplete) read '
                             'from a Response (r/o)')

    def __getservice_time2(self):
        if self.__service_time2 > 0.0:
            return self.__service_time2
        else:
            return 0.00000000001
    service_time2 = property(__getservice_time2, None, None,
                             'Duration in secods of the complete Request up '
                             'to now. Sum of all ``service_time1`` during '
                             'handling a Request (r/o)')

    def __getdebug_level(self):
        return self.__debuglevel
    def __setdebug_level(self, value):
        if type(value) != int or value not in range(0,10):
            raise ValueError('debug_level must be in range 0..9')
        self.__debuglevel = value
        if self.__con:
            self.__con.set_debuglevel(self.__debuglevel)
        self.logger.debug('debug_level set to {}'.format(self.__debuglevel))
    debug_level = property(__getdebug_level, __setdebug_level,
                           'The debug level used by underlying '
                           '*http.client.HTTP(S)Connection* object (r/w)')

    def __repr__(self):
        return('{}({}, timeout={}, idletime={}, retries={}, '
               'debuglevel={}, sock_keepalive={}, tcp_keepalive={}, '
               'tcp_keepintvl={}, tcp_keepcnt={})'
               .format(__class__.__name__, repr(self.__target), self.__timeout, self.__idletime,
                       self.__retries, self.__debuglevel, self.sock_keepalive,
                       self.tcp_keepalive, self.tcp_keepintvl,
                       self.tcp_keepcnt))

    def __str__(self):
        return ("{} initialized for fqdn {} @ {}"
                .format(__class__.__name__, self.__target.fqdn,
                        self.__address))


# helper functions
def checkport(target, port):
    """
    Check if an *hcpsdk.Target()* object is initialized with the correct port.

    :param target:  the *hcpsdk.Target()* object to check
    :param port:    the needed port
    :returns:       nothing
    :raises:        *hcpsdk.HcpsdkPortError* in case the port is invalid
    """
    logger = logging.getLogger(__name__)

    if target.port != port:
        raise HcpsdkPortError('Target initialized for port {}, not {}'
                              .format(target.port, port))

