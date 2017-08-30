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

import sys
import os.path
sys.path.insert(0, os.path.abspath('..'))
from hcpsdk import ips
import init_tests as it


class TestHcpsdk_10_1_Ips(unittest.TestCase):
    # def setUp(self):
    #     self.T_NS_GOOD = "n1.m.hcp1.snomis.local"
    #     self.T_NS_BAD = "this_wont_work.at-all"
    #     self.T_PORT = 443

    def test_1_05_query_good_fqdn(self):
        """
        Make sure we get a hcpsdk.Target object
        """
        print('test_1_05_query_good_fqdn')
        r = ips.query(it.P_NS_GOOD, cache=it.P_DNSCACHE)
        print(r)
        self.assertTrue(type(r) == ips.Response)
        self.assertTrue(type(r.ips) == list)
        print('fqdn: {} - cache = {}'.format(r.fqdn, r.cache))
        print(r.ips)

    def test_1_10_good_fqdn(self):
        """
        Make sure we get a hcpsdk.Target object
        """
        ipaddrqry = ips.Circle(fqdn=it.P_NS_GOOD, port=it.P_PORT, dnscache=it.P_DNSCACHE)
        self.assertTrue(ipaddrqry._addr() in ipaddrqry._addresses)

    def test_1_20_bad_fqdn(self):
        """
        Makes sure we raise hcpsdk.ips.ipsError on an invalid authority
        (which means, we can't resolve an IP address for it)
        """
        with self.assertRaises(ips.IpsError):
            ips.Circle(fqdn=it.P_NS_BAD, port=it.P_PORT, dnscache=it.P_DNSCACHE)


if __name__ == '__main__':
    unittest.main()
