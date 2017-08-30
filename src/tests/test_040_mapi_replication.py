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
from pprint import pprint

import hcpsdk
import init_tests as it


class LtVars(object):
    linkname = ''


class TestHcpsdk_40_1_Mapi_Replication(unittest.TestCase):
    def setUp(self):
        # self.T_NS_GOOD = "admin.hcp1.snomis.local"
        # self.T_USER = "service"
        # self.T_PASSWORD = "service01"
        # self.T_AUTH = hcpsdk.NativeAuthorization(self.T_USER, self.T_PASSWORD)
        # self.T_PORT = 9090
        self.hcptarget = hcpsdk.Target(it.P_ADMIN, it.P_ADMAUTH,
                                       port=it.P_MAPIPORT, dnscache=it.P_DNSCACHE)
        self.mapi = hcpsdk.mapi.Replication(self.hcptarget)

    def tearDown(self):
        del self.hcptarget

    def test_1_10_good_getReplicationSettings(self):
        """
        Make sure we get a list with at least one entry
        """
        print('test_1_10_good_getReplicationSettings:')
        r = self.mapi.getreplicationsettings()
        pprint(r)
        self.assertTrue(type(r) == dict)

    def test_1_20_good_getLinkList(self):
        """
        Make sure we get a list with at least one entry
        """
        print('test_1_20_good_getLinkList:')
        r = self.mapi.getlinklist()
        print(r)
        self.assertTrue(type(r) == list)
        self.assertTrue(len(r) >= 1)
        LtVars.linkname = r[0]

    def test_1_30_good_getLinkDetails(self):
        """
        Make sure we get a list with at least one entry
        """
        print('test_1_30_good_getLinkDetails({}):'.format(LtVars.linkname))
        r = self.mapi.getlinkdetails(link=LtVars.linkname)
        pprint(r)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
