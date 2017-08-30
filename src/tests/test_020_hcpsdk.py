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
import os.path
sys.path.insert(0, os.path.abspath('..'))
import hcpsdk
from hcpsdk.ips import IpsError
import unittest
import ssl
import socket
import http.client
from pprint import pprint

import init_tests as it

print('hcpsdk: ', hcpsdk.version())



# @unittest.skip("skip TestHcpsdk_01_Target")
class TestHcpsdk_01_Target(unittest.TestCase):

    def test_01_10_ip_address_available(self):
        """
        Make sure we can get a single IP address from Target object's pool
        """
        hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, port=it.P_PORT,
                                  dnscache=it.P_DNSCACHE)
        self.assertTrue(hcptarget.getaddr() in hcptarget.addresses)

    def test_01_20_ip_address_not_available(self):
        """
        Make sure an exception is raised if the FQDN can't be resolved
        """
        with self.assertRaises(hcpsdk.ips.IpsError):
            hcpsdk.Target(it.P_NS_BAD, it.P_AUTH, port=it.P_PORT,
                          dnscache=it.P_DNSCACHE)

    def test_01_30_good_target_authority(self):
        """
        Make sure we get a hcpsdk.Target object
        """
        hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, port=it.P_PORT,
                                  dnscache=it.P_DNSCACHE)
        self.assertIs(type(hcptarget), hcpsdk.Target)


# @unittest.skip("skip TestHcpsdk_02_Access_http")
class TestHcpsdk_02_Access_http(unittest.TestCase):
    '''
    Make sure we can write/head/post/delete a file using http
    '''
    def setUp(self):
        self.T_HCPFILE = '/rest/hcpsdk/TestHCPsdk_20_access'
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, it.P_PORT,
                                       dnscache=it.P_DNSCACHE)
        self.con = hcpsdk.Connection(self.hcptarget)

    def tearDown(self):
        self.con.close()
        del self.hcptarget

    def test_02_10_put(self):
        """
        Ingest a file
        """
        # noinspection PyPep8Naming
        T_BUF = '0123456789ABCDEF' * 64
        r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.assertEqual(r.status, 201)

    def test_02_20_head(self):
        """
        Delete a file
        """
        r = self.con.HEAD(self.T_HCPFILE)
        self.assertEqual(r.status, 200)

    def test_02_30_post(self):
        """
        Delete a file
        """
        r = self.con.POST(self.T_HCPFILE, params={'index': 'true'})
        self.assertEqual(r.status, 200)

    def test_02_90_delete(self):
        """
        Delete a file
        """
        r = self.con.DELETE(self.T_HCPFILE)
        self.assertEqual(r.status, 200)


# @unittest.skip("skip TestHcpsdk_03_Access_Fail")
class TestHcpsdk_03_Access_Fail(unittest.TestCase):
    '''
    Make sure we fail when trying to read a non-existant file
    not verifying the cert at all.
    '''
    def setUp(self):
        self.T_HCPFILE = '/rest/hcpsdk/fail_TestHCPsdk_20_access'
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, it.P_SSLPORT,
                                       dnscache=it.P_DNSCACHE)
        self.con = hcpsdk.Connection(self.hcptarget)

    def tearDown(self):
        self.con.close()
        del self.hcptarget

    def test_03_10_get(self):
        """
        Read a file
        """
        self.r = self.con.GET(self.T_HCPFILE)
        self.assertEqual(self.r.status, 404)


# @unittest.skip("skip TestHcpsdk_10_Errors")
class TestHcpsdk_10_Errors(unittest.TestCase):
    '''
    Make sure we get the proper error if an ConnectionAbortedError is raised
    '''
    def setUp(self):
        self.T_HCPFILE = '/rest/hcpsdk/TestHCPsdk_20_access'
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, it.P_SSLPORT,
                                       dnscache=it.P_DNSCACHE)
        self.con = hcpsdk.Connection(self.hcptarget, retries=1)

    def tearDown(self):
        r = self.con.DELETE(self.T_HCPFILE)
        self.con.close()
        del self.hcptarget

    def test_10_09_IpsError(self):
        """
        Ingest a file while forcing an error
        """
        T_BUF = '0123456789ABCDEF' * 64
        r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.assertEqual(r.status, 201)

        self.con._fail = IpsError
        self.assertRaises(IpsError, self.con.HEAD, self.T_HCPFILE)

    def test_10_10_ConnectionAbortedError(self):
        """
        Ingest a file while forcing an error
        """
        T_BUF = '0123456789ABCDEF' * 64
        r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.assertEqual(r.status, 201)

        self.con._fail = ConnectionAbortedError
        r = self.con.HEAD(self.T_HCPFILE)
        self.assertEqual(r.status, 200)

    def test_10_11_TimeoutError(self):
        """
        Ingest a file while forcing an error
        """
        T_BUF = '0123456789ABCDEF' * 64
        r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.assertEqual(r.status, 201)

        self.con._fail = TimeoutError
        r = self.con.HEAD(self.T_HCPFILE)
        self.assertEqual(r.status, 200)

    def test_10_12_sockettimeout(self):
        """
        Ingest a file while forcing an error
        """
        T_BUF = '0123456789ABCDEF' * 64
        r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.assertEqual(r.status, 201)

        self.con._fail = socket.timeout
        r = self.con.HEAD(self.T_HCPFILE)
        self.assertEqual(r.status, 200)

    def test_10_13_httpclientResponseNotReady(self):
        """
        Ingest a file while forcing an error
        """
        T_BUF = '0123456789ABCDEF' * 64
        r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.assertEqual(r.status, 201)

        self.con._fail = http.client.ResponseNotReady
        r = self.con.HEAD(self.T_HCPFILE)
        self.assertEqual(r.status, 200)

    def test_10_14_HcpsdkCertificateError(self):
        """
        Ingest a file while forcing an error
        """
        T_BUF = '0123456789ABCDEF' * 64
        r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.assertEqual(r.status, 201)

        self.con._fail = ssl.SSLError
        self.assertRaises(hcpsdk.HcpsdkCertificateError, self.con.HEAD, self.T_HCPFILE)

    def test_10_15_httpclientHTTPException(self):
        """
        Ingest a file while forcing an error
        """
        T_BUF = '0123456789ABCDEF' * 64
        r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.assertEqual(r.status, 201)

        self.con._fail = http.client.HTTPException
        self.assertRaises(hcpsdk.HcpsdkError, self.con.HEAD, self.T_HCPFILE)



if __name__ == '__main__':
    unittest.main()
