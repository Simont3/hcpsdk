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

import logging
import socket
from http.client import HTTPConnection as _HTTPConnection, HTTPS_PORT

__all__ = ['HTTPConnection']

# from netinet/tcp.h:
#   define TCP_KEEPALIVE   0x10    /* idle time used when SO_KEEPALIVE is enabled */
#   The TCP_KEEPALIVE options enable to specify the amount of time, in
#   seconds, that the connection must be idle before keepalive probes
#   (if enabled) are sent.  The default value is specified by the MIB
#   variable net.inet.tcp.keepidle.
TCP_KEEPALIVE = 0x10
# from netinet/tcp.h:
#   define	TCP_KEEPINTVL	0x101	/* interval between keepalives */
#   When keepalive probes are enabled, this option will set the amount
#   of time in seconds between successive keepalives sent to probe an
#   unresponsive peer.
TCP_KEEPINTVL = 0x101
# from netinet/tcp.h:
#   define	TCP_KEEPCNT		0x102	/* number of keepalives before close */
#   When keepalive probes are enabled, this option will set the number
#   of times a keepalive probe should be repeated if the peer is not
#   responding. After this many probes, the connection will be closed.
TCP_KEEPCNT = 0x102

logging.getLogger('hcpsdk.httpclient').addHandler(logging.NullHandler())


class HTTPConnection(_HTTPConnection):
    """
    Subclass of http.client.HTTPConnection that allows for TCP keep-alive.

    This copies the *__init__()* and *connect()* methods, adding in the
    necessary code to enable TCP keep-alive.
    """

    def __init__(self, host, port=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=None, sock_keepalive=False,
                 tcp_keepalive=60, tcp_keepintvl=60, tcp_keepcnt=3):
        """
        :param host:            target host (fqdn or ip-address
        :param port:            target port
        :param timeout:         blocking calls time-out
        :param source_address:  source address tuple (ip. port) to be used
        :param sock_keepalive:  enable TCP keepalive, if True
        :param tcp_keepalive:   idle time used when SO_KEEPALIVE is enable
        :param tcp_keepintvl:   interval between keepalives
        :param tcp_keepcnt:     number of keepalives before close
        """

        self.logger = logging.getLogger(__name__ + '.HTTPConnection')
        self.sock_keepalive = sock_keepalive
        self.tcp_keepalive = tcp_keepalive
        self.tcp_keepintvl = tcp_keepintvl
        self.tcp_keepcnt = tcp_keepcnt
        super().__init__(host, port, timeout=timeout,
                         source_address=source_address)

    def connect(self):
        """
        Connect to the host and port specified in __init__, using the
        keep-alive settings specified there as well.
        """
        self.sock = self._create_connection(
            (self.host,self.port), self.timeout, self.source_address)

        # added to standard method:
        if self.sock_keepalive:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.sock.setsockopt(socket.SOL_TCP, TCP_KEEPALIVE, self.tcp_keepalive)
            self.sock.setsockopt(socket.SOL_TCP, TCP_KEEPINTVL, self.tcp_keepintvl)
            self.sock.setsockopt(socket.SOL_TCP, TCP_KEEPCNT, self.tcp_keepcnt)

            self.logger.debug('enabled TCP keep-alive (TCP_KEEPALIVE = {}, '
                              'TCP_KEEPINTVL = {}, TCP_KEEPCNT = {})'
                              .format(self.sock.getsockopt(socket.SOL_TCP,
                                                           TCP_KEEPALIVE),
                                      self.sock.getsockopt(socket.SOL_TCP,
                                                           TCP_KEEPINTVL),
                                      self.sock.getsockopt(socket.SOL_TCP,
                                                           TCP_KEEPCNT)))
        # end of addition

        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if self._tunnel_host:
            self._tunnel()


try:
    import ssl
except ImportError:
    pass
else:
    class HTTPSConnection(_HTTPConnection):
        "This class allows communication via SSL."

        default_port = HTTPS_PORT

        # XXX Should key_file and cert_file be deprecated in favour of context?

        def __init__(self, host, port=None, key_file=None, cert_file=None,
                     timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                     source_address=None, *, context=None,
                     check_hostname=None, sock_keepalive=False,
                     tcp_keepalive=60, tcp_keepintvl=60, tcp_keepcnt=3):
            """
            :param host:            target host (fqdn or ip-address
            :param port:            target port
            :param timeout:         blocking calls time-out
            :param source_address:  source address tuple (ip. port) to be used
            :param sock_keepalive:  enable TCP keepalive, if True
            :param tcp_keepalive:   idle time used when SO_KEEPALIVE is enable
            :param tcp_keepintvl:   interval between keepalives
            :param tcp_keepcnt:     number of keepalives before close
            """
            # added to standard method:
            self.logger = logging.getLogger(__name__ + '.HTTPConnection')
            self.sock_keepalive = sock_keepalive
            self.tcp_keepalive = tcp_keepalive
            self.tcp_keepintvl = tcp_keepintvl
            self.tcp_keepcnt = tcp_keepcnt
            # end of addition

            super(HTTPSConnection, self).__init__(host, port, timeout,
                                                  source_address)
            self.key_file = key_file
            self.cert_file = cert_file
            if context is None:
                context = ssl._create_default_https_context()
            will_verify = context.verify_mode != ssl.CERT_NONE
            if check_hostname is None:
                check_hostname = context.check_hostname
            if check_hostname and not will_verify:
                raise ValueError("check_hostname needs a SSL context with "
                                 "either CERT_OPTIONAL or CERT_REQUIRED")
            if key_file or cert_file:
                context.load_cert_chain(cert_file, key_file)
            self._context = context
            self._check_hostname = check_hostname

        def connect(self):
            "Connect to a host on a given (SSL) port."

            super().connect()

            # added to standard method:
            if self.sock_keepalive:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.sock.setsockopt(socket.SOL_TCP, TCP_KEEPALIVE, self.tcp_keepalive)
                self.sock.setsockopt(socket.SOL_TCP, TCP_KEEPINTVL, self.tcp_keepintvl)
                self.sock.setsockopt(socket.SOL_TCP, TCP_KEEPCNT, self.tcp_keepcnt)

                self.logger.debug('enabled TCP keep-alive (TCP_KEEPALIVE = {}, '
                                  'TCP_KEEPINTVL = {}, TCP_KEEPCNT = {})'
                                  .format(self.sock.getsockopt(socket.SOL_TCP,
                                                               TCP_KEEPALIVE),
                                          self.sock.getsockopt(socket.SOL_TCP,
                                                               TCP_KEEPINTVL),
                                          self.sock.getsockopt(socket.SOL_TCP,
                                                               TCP_KEEPCNT)))
            # end of addition

            if self._tunnel_host:
                server_hostname = self._tunnel_host
            else:
                server_hostname = self.host

            self.sock = self._context.wrap_socket(self.sock,
                                                  server_hostname=server_hostname)
            if not self._context.check_hostname and self._check_hostname:
                try:
                    ssl.match_hostname(self.sock.getpeercert(), server_hostname)
                except Exception:
                    self.sock.shutdown(socket.SHUT_RDWR)
                    self.sock.close()
                    raise

    __all__.append("HTTPSConnection")
