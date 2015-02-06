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

import unittest
import hcpsdk
import ssl
import http.client
from pprint import pprint

import tests.init_tests as it


class TestHcpsdk_1_Target(unittest.TestCase):

    def test_1_10_ip_address_available(self):
        """
        Make sure we can get a single IP address from Target object's pool
        """
        hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, port=it.P_PORT, dnscache=it.P_DNSCACHE)
        self.assertTrue(hcptarget.getaddr() in hcptarget.addresses)

    def test_1_20_ip_address_not_available(self):
        """
        Make sure an exception is raised if the FQDN can't be resolved
        """
        with self.assertRaises(hcpsdk.HcpsdkError):
            hcpsdk.Target(it.P_NS_BAD, it.P_AUTH, port=it.P_PORT, dnscache=it.P_DNSCACHE)

    def test_1_30_good_target_authority(self):
        """
        Make sure we get a hcpsdk.Target object
        """
        hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, port=it.P_PORT, dnscache=it.P_DNSCACHE)
        self.assertIs(type(hcptarget), hcpsdk.Target)

    def test_1_40_bad_target_authority(self):
        """
        Makes sure we raise hcpsdk.HcpsdkError on an invalid authority
        (which means, we can't resolve an IP address for it)
        """
        with self.assertRaises(hcpsdk.HcpsdkError):
            hcpsdk.Target(it.P_NS_BAD, it.P_AUTH, port=it.P_PORT, dnscache=it.P_DNSCACHE)


# @unittest.skip("demonstrating skipping")
class TestHcpsdk_2_Access_http(unittest.TestCase):
    def setUp(self):
        self.T_HCPFILE = '/rest/hcpsdk/TestHCPsdk_20_access'
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, it.P_PORT, dnscache=it.P_DNSCACHE)
        self.con = hcpsdk.Connection(self.hcptarget)

    def tearDown(self):
        self.con.close()
        del self.hcptarget

    def test_2_10_put(self):
        """
        Ingest a file
        """
        # noinspection PyPep8Naming
        T_BUF = '0123456789ABCDEF' * 64
        r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.assertEqual(r.status, 201)

    def test_2_20_head(self):
        """
        Delete a file
        """
        r = self.con.HEAD(self.T_HCPFILE)
        self.assertEqual(r.status, 200)

    def test_2_30_post(self):
        """
        Delete a file
        """
        r = self.con.POST(self.T_HCPFILE, {'index': 'true'})
        self.assertEqual(r.status, 200)

    def test_2_90_delete(self):
        """
        Delete a file
        """
        r = self.con.DELETE(self.T_HCPFILE)
        self.assertEqual(r.status, 200)


# @unittest.skip("demonstrating skipping")
class TestHcpsdk_3_Access_https_success(unittest.TestCase):
    def setUp(self):
        self.T_HCPFILE = '/rest/hcpsdk/TestHCPsdk_20_access'
        self.ctxt = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH,
                                               cafile='certs/rootCertificate.pem')
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, it.P_PORT,
                                       dnscache=it.P_DNSCACHE, sslcontext=self.ctxt)
        self.con = hcpsdk.Connection(self.hcptarget)

    def tearDown(self):
        self.con.close()
        del self.hcptarget

    def test_3_10_put(self):
        """
        Ingest a file
        """
        # noinspection PyPep8Naming
        T_BUF = '0123456789ABCDEF' * 64
        r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.assertEqual(r.status, 201)

    def test_3_20_head(self):
        """
        Delete a file
        """
        r = self.con.HEAD(self.T_HCPFILE)
        self.assertEqual(r.status, 200)

    def test_3_30_post(self):
        """
        Delete a file
        """
        r = self.con.POST(self.T_HCPFILE, {'index': 'true'})
        self.assertEqual(r.status, 200)

    def test_3_90_delete(self):
        """
        Delete a file
        """
        r = self.con.DELETE(self.T_HCPFILE)
        self.assertEqual(r.status, 200)


# @unittest.skip("demonstrating skipping")
class TestHcpsdk_4_Access_https_fail(unittest.TestCase):
    def setUp(self):
        self.T_HCPFILE = '/rest/hcpsdk/TestHCPsdk_20_access'
        self.ctxt = ssl.create_default_context()
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, it.P_PORT,
                                       dnscache=it.P_DNSCACHE, sslcontext=self.ctxt)
        self.con = hcpsdk.Connection(self.hcptarget)

    def tearDown(self):
        self.con.close()
        del self.hcptarget

    def test_4_10_put(self):
        """
        Ingest a file
        """
        # noinspection PyPep8Naming
        T_BUF = '0123456789ABCDEF' * 64
        with self.assertRaises(hcpsdk.HcpsdkError):
            r = self.con.PUT(self.T_HCPFILE, T_BUF)

    def test_4_90_delete(self):
        """
        Delete a file
        """
        with self.assertRaises(hcpsdk.HcpsdkError):
            r = self.con.DELETE(self.T_HCPFILE)


# @unittest.skip("demonstrating skipping")
class TestHcpsdk_5_Access_Fail(unittest.TestCase):
    def setUp(self):
        self.T_HCPFILE = '/rest/hcpsdk/TestHCPsdk_20_access'
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, it.P_PORT, dnscache=it.P_DNSCACHE)
        self.con = hcpsdk.Connection(self.hcptarget)

    def tearDown(self):
        self.con.close()
        self.con = hcpsdk.Connection(self.hcptarget)
        self.con.DELETE(self.T_HCPFILE)
        self.con.close()
        del self.hcptarget

    def test_5_10_put(self):
        """
        Ingest a file
        """
        # noinspection PyPep8Naming
        T_BUF = '0123456789ABCDEF' * 64
        self.r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.r.read()
        self.assertEqual(self.r.status, 201)

        self.r = self.con.GET(self.T_HCPFILE)
        # self.r.read()
        self.assertEqual(self.r.status, 200)

        with self.assertRaises(http.client.ResponseNotReady):
            self.r = self.con.HEAD(self.T_HCPFILE)


if __name__ == '__main__':
    unittest.main()