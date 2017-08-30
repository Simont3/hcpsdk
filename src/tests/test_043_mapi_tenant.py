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
import logging
import sys
from pprint import pprint

import hcpsdk
import init_tests as it


class TestHcpsdk_43_1_Mapi_Tenant(unittest.TestCase):
    def setUp(self):
        sh = logging.StreamHandler(sys.stderr)
        fh = logging.Formatter("[%(levelname)-8s]: %(message)s")
        sh.setFormatter(fh)
        log = logging.getLogger()
        log.addHandler(sh)
        log.setLevel(logging.INFO)

        self.hcptarget = hcpsdk.Target(it.P_ADMIN, it.P_ADMAUTH,
                                       port=it.P_MAPIPORT, dnscache=False)

    def tearDown(self):
        del self.hcptarget

    def test_1_10_tenant_list(self):
        """
        Check if we can list all Tenants
        """
        print('test_1_10_tenant_list:')

        tenants = hcpsdk.mapi.listtenants(self.hcptarget, debuglevel=0)
        self.assertTrue(type(tenants) == list)

        for i in tenants:
            self.assertTrue(type(i) == hcpsdk.mapi.Tenant)
            pprint(i.info())
            i.close()

