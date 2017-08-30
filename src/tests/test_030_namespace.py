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

import unittest
from collections import OrderedDict
from pprint import pprint

import hcpsdk
import init_tests as it

import logging
logging.basicConfig(filename='_example.log', level=logging.DEBUG)


class TestHcpsdk_30_1_NamespaceInfo_NS_GOOD(unittest.TestCase):
    def setUp(self):
        # self.T_NS_GOOD = "n1.m.hcp1.snomis.local"
        # self.T_USER = "n"
        # self.T_PASSWORD = "n01"
        # self.T_AUTH = hcpsdk.NativeAuthorization(self.T_USER, self.T_PASSWORD)
        # self.T_PORT = 443
        self.hcptarget = hcpsdk.Target(it.P_NS_GOOD, it.P_AUTH, port=it.P_PORT, dnscache=it.P_DNSCACHE)
        self.nso = hcpsdk.namespace.Info(self.hcptarget)

    def tearDown(self):
        del self.hcptarget

    # @unittest.skip("demonstrating skipping")
    def test_1_10_good_NSstatistics(self):
        """
        Make sure we get a dict w/ length 9
        """
        print('test_1_10_good_NSstatistics')
        r = self.nso.nsstatistics()
        pprint(r)
        self.assertTrue(type(r) == dict)
        self.assertTrue(len(r) == 9)

    # @unittest.skip("demonstrating skipping")
    def test_1_20_good_listAccessibleNS(self):
        """
        Make sure we get a dict holding dicts
        """
        print('test_1_20_good_listAccessibleNS')
        r = self.nso.listaccessiblens()
        pprint(r)
        self.assertTrue(type(r) == OrderedDict)
        for ns in r:
            self.assertTrue(type(r[ns]) == dict)

    def test_1_30_good_listThisNSonly(self):
        print('test_1_30_good_listThisNSonly')
        r = self.nso.listaccessiblens(all=False)
        pprint(r)
        self.assertTrue(type(r) == OrderedDict)
        self.assertTrue(len(r) == 1)
        for ns in r:
            self.assertTrue(type(r[ns]) == dict)

        #    @unittest.skip("demonstrating skipping")

    def test_1_40_good_listRetentionClasses(self):
        r = self.nso.listretentionclasses()
        pprint(r)
        self.assertTrue(type(r) == OrderedDict)
        for ns in r:
            self.assertTrue(type(r[ns]) == dict)

        #    @unittest.skip("demonstrating skipping")

    def test_1_50_good_listPermissions(self):
        print('test_1_50_good_listPermissions')
        r = self.nso.listpermissions()
        pprint(r)
        self.assertTrue(type(r) == OrderedDict)
        for ns in r:
            self.assertTrue(type(r[ns]) == dict)
        for nsk in r.keys():
            self.assertTrue(nsk in ['namespacePermissions',
                                    'namespaceEffectivePermissions',
                                    'userPermissions',
                                    'userEffectivePermissions'])


if __name__ == '__main__':
    unittest.main()
