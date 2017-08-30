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
print(hcpsdk.version())
import unittest
import ssl
from pprint import pprint

import init_tests as it


# @unittest.skip("skip TestHcpsdk_3_Access_https_certfile")
class TestHcpsdk_1_Access_https_certfile(unittest.TestCase):
    '''
    Make sure we can write/head/post/delete a file using https,
    verifying the cert against a local rootCertificate.
    '''
    def setUp(self):
        print('>>> TestHcpsdk_1_Access_https_certfile:')
        self.T_HCPFILE = '/rest/hcpsdk/TestHCPsdk_20_access'
        self.ctxt = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH,
                                               cafile='certs/rootCertificate.pem')
        print('Certificate store status:')
        pprint(self.ctxt.cert_store_stats())
        print('CA certificates:')
        pprint((self.ctxt.get_ca_certs()))
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, it.P_SSLPORT,
                                       dnscache=it.P_DNSCACHE, sslcontext=self.ctxt)
        self.con = hcpsdk.Connection(self.hcptarget)

    def tearDown(self):
        self.con.close()
        del self.hcptarget

    def test_1_10_put(self):
        """
        Ingest a file
        """
        # noinspection PyPep8Naming
        T_BUF = '0123456789ABCDEF' * 64
        r = self.con.PUT(self.T_HCPFILE, T_BUF)
        self.assertEqual(r.status, 201)

    def test_1_20_head(self):
        """
        Delete a file
        """
        r = self.con.HEAD(self.T_HCPFILE)
        self.assertEqual(r.status, 200)

    def test_1_30_post(self):
        """
        Delete a file
        """
        r = self.con.POST(self.T_HCPFILE, {'index': 'true'})
        self.assertEqual(r.status, 200)

    def test_1_90_delete(self):
        """
        Delete a file
        """
        r = self.con.DELETE(self.T_HCPFILE)
        self.assertEqual(r.status, 200)


# @unittest.skip("skip TestHcpsdk_4_Access_https_systemCA")
class TestHcpsdk_2_Access_https_systemCA(unittest.TestCase):
    '''
    Make sure we can write/head/post/delete a file using https,
    verifying the cert against the systems CA store.
    '''
    def setUp(self):
        print('>>> TestHcpsdk_2_Access_https_systemCA:')
        self.T_HCPFILE = '/rest/hcpsdk/TestHCPsdk_20_access'
        self.ctxt = ssl.create_default_context()
        print('Certificate store status:')
        pprint(self.ctxt.cert_store_stats())
        print('CA certificates:')
        pprint((self.ctxt.get_ca_certs()))
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, it.P_SSLPORT,
                                       dnscache=it.P_DNSCACHE, sslcontext=self.ctxt)
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
        print(self.con.response_status, self.con.response_reason)
        self.assertEqual(r.status, 201)

    def test_2_90_delete(self):
        """
        Delete a file
        """
        r = self.con.DELETE(self.T_HCPFILE)
        print(self.con.response_status, self.con.response_reason)
        self.assertEqual(r.status, 200)


# @unittest.skip("demonstrating skipping")
class TestHcpsdk_3_Access_https_certfile_fail(unittest.TestCase):
    '''
    Make sure we fail write/delete a file using https,
    verifying the cert against a false rootCertificate.
    '''
    def setUp(self):
        print('>>> TestHcpsdk_3_Access_https_certfile_fail:')
        self.T_HCPFILE = '/rest/hcpsdk/TestHCPsdk_20_access'
        self.ctxt = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH,
                                               cafile='certs/failCertificate.pem')
        print('Certificate store status:')
        pprint(self.ctxt.cert_store_stats())
        print('CA certificates:')
        pprint((self.ctxt.get_ca_certs()))
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, it.P_SSLPORT,
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
        with self.assertRaises(hcpsdk.HcpsdkCertificateError):
            r = self.con.PUT(self.T_HCPFILE, T_BUF)

    def test_3_90_delete(self):
        """
        Delete a file
        """
        with self.assertRaises(hcpsdk.HcpsdkCertificateError):
            r = self.con.DELETE(self.T_HCPFILE)


# @unittest.skip("demonstrating skipping")
class TestHcpsdk_4_Access_Fail(unittest.TestCase):
    '''
    Make sure we fail when trying to read a non-existant file
    not verifying the cert at all.
    '''
    def setUp(self):
        self.T_HCPFILE = '/rest/hcpsdk/fail_TestHCPsdk_20_access'
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, it.P_SSLPORT, dnscache=it.P_DNSCACHE)
        self.con = hcpsdk.Connection(self.hcptarget)

    def tearDown(self):
        self.con.close()
        del self.hcptarget

    def test_4_10_get(self):
        """
        Ingest a file
        """
        self.r = self.con.GET(self.T_HCPFILE)
        print(self.con.response_status, self.con.response_reason)
        self.assertEqual(self.r.status, 404)


if __name__ == '__main__':
    unittest.main()
