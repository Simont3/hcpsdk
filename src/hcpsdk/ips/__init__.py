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

import threading
import socket
import logging
# noinspection PyPackageRequirements
import dns
# noinspection PyPackageRequirements
import dns.resolver


__all__ = ['IpsError', 'Circle', 'Request', 'Response', 'query']

logging.getLogger('hcpsdk.ips').addHandler(logging.NullHandler())


class IpsError(Exception):
    """
    Signal an error in *hcpsdk.ips* - typically a name resolution problem.
    """

    def __init__(self, reason):
        """
        :param reason:  an error description
        """
        self.args = (reason,)


# noinspection PyTypeChecker
class Circle(object):
    """
    Resolve an FQDN (using **query()**), cache the acquired IP addresses and
    yield them round-robin.
    """
    __EMPTY_ADDRLIST = []

    def __init__(self, fqdn, port=443, dnscache=False):
        """
        :param fqdn:        the FQDN to be resolved
        :param port:        the port to be used by the **hcpsdk.Target** object
        :param dnscache:    if True, use the system resolver (which **might** do
                            local caching), else use an internal resolver,
                            bypassing any cache available
        :returns:           an *hcpsdk.ips.Response* object
        """
        self.logger = logging.getLogger(__name__ + '.Circle')
        self.__authority = fqdn
        self.__port = port
        self.__dnscache = dnscache
        self._cLock = threading.Lock()
        self.__generator = None
        self._addresses = Circle.__EMPTY_ADDRLIST.copy()
        self.logger = logging.getLogger('hcpsdk.ips.Circle')

        # initial lookup, build the address cache
        self._addr(fqdn=self.__authority)

    def _addr(self, fqdn=None):
        """
        If called with a dnsname (FQDN), query DNS for that name,
        cache the acquired IP addresses.
        If called without dnsname, work as a generator that yields the
        cached IP addresses in a round-robin fashion.

        .. Warning::
            This method is intended to be internal to **hcpsdk** and may be used
            from the outside *without* parameters, only.

        :param fqdn:    the FQDN
        :return:        an IP address (as string)
        """

        def __addr(dnsname, dnscache=False):
            """
            resolve HCPs IP addresses and build a list with all IPs gathered
            """
            self._addresses = Circle.__EMPTY_ADDRLIST.copy()
            result = query(dnsname, cache=dnscache)
            if result.raised:
                raise IpsError(result.raised)
            self._addresses = result.ips.copy()

            while True:
                for ipadr in self._addresses:
                    yield str(ipadr)

        # acquire a lock to make sure that one Request gets serviced at a time
        self._cLock.acquire()
        if fqdn:
            self.__generator = __addr(fqdn, dnscache=self.__dnscache)
        myaddr = next(self.__generator)
        self._cLock.release()
        if fqdn:
            self.logger.debug('(re-) loaded IP address cache: {}, dnscache = {}'
                              .format(self._addresses, self.__dnscache))
        self.logger.debug('issued IP address: {}'.format(myaddr))
        return myaddr

    def refresh(self):
        """
        Force a fresh DNS query and rebuild the cached list of IP addresses
        """
        self._addr(fqdn=self.__authority)
        self.logger.debug('IP address cache refreshed')

    def __getattr__(self, item):
        """
        Used to make _addresses a read-only attributes
        """
        if item == '_addresses':
            return self._addresses
        else:
            raise AttributeError

    def __str__(self):
        return self.answer.qname


class Request(object):
    """
    A DNS query Request object
    """

    def __init__(self, fqdn, cache):
        self.fqdn = fqdn
        self.cache = cache
        self.sub = None


class Response(object):
    """
    DNS query Response object, returned by the **query()** function.
    """

    def __init__(self, fqdn, cache):
        """
        :param fqdn:    the FQDN for the Response
        :param cache:   Response from a query by-passing the local DNS cache (False)
                        or using the system resolver (True)
        """
        self.fqdn = fqdn
        self.cache = cache
        self.ips = []
        self.raised = ''


def query(fqdn, cache=False):
    """
    Submit a DNS query, using *socket.getaddrinfo()* if cache=True, or
    *dns.resolver.query()* if cache=False.

    :param fqdn:    a FQDN to query DNS -or- a *Request* object
    :param cache:   if True, use the system resolver (which might do local caching),
                    else use an internal resolver, bypassing any cache available
    :return:        an **hcpsdk.ips.Response** object
    :raises:        should never raise, as Exceptions are signaled through
                    the **Response.raised** attribute
    """
    if isinstance(fqdn, Request):
        _response = Response(fqdn.fqdn, fqdn.cache)  # to collect the resolved IP addresses
    else:
        _response = Response(fqdn, cache)  # to collect the resolved IP addresses

    if _response.cache:
        try:
            ips = socket.getaddrinfo(_response.fqdn, 443, family=socket.AF_INET, type=socket.SOCK_DGRAM)
        except Exception as e:
            _response.raised = 'Err: ' + str(e)
        else:
            for a in ips:
                if a[4][0] not in _response.ips:
                    _response.ips.append(a[4][0])
    else:
        try:
            ips = dns.resolver.query(_response.fqdn, raise_on_no_answer=True)
        except dns.resolver.NXDOMAIN:
            _response.raised = 'Err: NXDOMAIN - The query name does not exist.'
        except dns.resolver.YXDOMAIN:
            _response.raised = 'Err: The query name is too long after DNAME substitution.'
        except dns.resolver.Timeout:
            _response.raised = 'Err: The operation timed out.'
        except dns.resolver.NoAnswer:
            _response.raised = 'Err: The Response did not contain an answer to the question.'
        except dns.resolver.NoNameservers:
            _response.raised = 'Err: NoNameservers - No non-broken nameservers are available to answer the query.'
        except dns.resolver.NotAbsolute:
            _response.raised = 'Err: Raised if an absolute domain name is required but a relative name was provided.'
        except dns.resolver.NoRootSOA:
            _response.raised = 'Err: Raised if for some reason there is no SOA at the root name. ' \
                               'This should never happen!'
        except dns.resolver.NoMetaqueries:
            _response.raised = 'Err: Metaqueries are not allowed.'
        except Exception as e:
            _response.raised = 'Err: ' + str(e)
        else:
            for i in ips.rrset:
                ip = str(i)
                if ip[1] == '#':
                    hx = ip[-8:]
                    ip = '{}.{}.{}.{}'.format(int(hx[:2], 16), int(hx[2:4], 16),
                                              int(hx[4:6], 16), int(hx[6:], 16))
                _response.ips.append(str(ip))
            if not len(_response.ips):
                _response.raised = 'Err: no Response'

    return _response

