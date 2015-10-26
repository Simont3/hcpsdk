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
from pprint import pprint

import hcpsdk
from datetime import datetime
import init_tests as it


class TestHcpsdk_41_1_Mapi_Chargeback(unittest.TestCase):
    def setUp(self):
        self.hcptarget = hcpsdk.Target(it.L_ADMIN, it.L_ADMAUTH,
                                       port=it.L_MAPIPORT, dnscache=it.L_DNSCACHE)
        self.cb = hcpsdk.mapi.ChargeBack(self.hcptarget)

    def tearDown(self):
        self.cb.close()
        del self.hcptarget

    def test_1_10_chargeback_tenant_totals(self):
        """
        Check if we can load all Tenants totals
        """
        print('test_1_10_chargeback_tenant_totals:')

        l = self.cb.request(start=datetime(1970), end=datetime.now(),
                            intervall=hcpsdk.mapi.ChargeBack.C_TOTAL)
        pprint(l, indent=4)




        # self.assertTrue(l[0] == date(1970,1,1))
        # self.assertTrue(l[1] == date.today())
        # print('\tno date parameters: pass')
        #
        # l = self.logs.prepare(startdate=date.today() - timedelta(days=10),
        #                       enddate=date.today() - timedelta(days=1),
        #                       snodes=['s01','s02','s03'])
        # pprint(l, indent=4)
        # self.assertTrue(l[1] - l[0] == timedelta(days=9))
        # print('\tpast 10 days: pass')
        #
        # with self.assertRaises(ValueError):
        #      l = self.logs.prepare(startdate='10/10/2014',
        #                            enddate='12/31/2099')
        # print('\t\tstartdate: pass')
        # with self.assertRaises(ValueError):
        #      l = self.logs.prepare(startdate=date.today()-timedelta(days=10),
        #                            enddate='12/31/2099')
        # print('\t\tenddate: pass')
        # with self.assertRaises(ValueError):
        #      l = self.logs.prepare(startdate=date.today()-timedelta(days=10),
        #                            enddate=date.today() - timedelta(days=1),
        #                            snodes=('s01','s02','s03'))
        # print('\t\tsnodes: pass')
        # print('\tfalse paramaters: pass')
        #
