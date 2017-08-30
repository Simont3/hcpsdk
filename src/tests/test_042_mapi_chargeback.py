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
import json
from _io import StringIO

import hcpsdk
from datetime import datetime, timedelta
import init_tests as it


class TestHcpsdk_41_1_Mapi_Chargeback(unittest.TestCase):
    def setUp(self):
        sh = logging.StreamHandler(sys.stderr)
        fh = logging.Formatter("[%(levelname)-8s]: %(message)s")
        sh.setFormatter(fh)
        log = logging.getLogger()
        log.addHandler(sh)
        log.setLevel(logging.INFO)

        self.hcptarget = hcpsdk.Target(it.L_ADMIN, it.L_ADMAUTH,
                                       port=it.L_MAPIPORT, dnscache=it.L_DNSCACHE)
        self.cb = hcpsdk.mapi.ChargeBack(self.hcptarget)

    def tearDown(self):
        self.cb.close()
        del self.hcptarget

    def test_1_10_chargeback_tenant_totals_json(self):
        """
        Check if we can load all Tenants totals
        """
        print('test_1_10_chargeback_tenant_totals_json:')

        l = self.cb.request(tenant='m', start=datetime.now()-timedelta(days=10),
                            end=datetime.now(),
                            granularity=hcpsdk.mapi.ChargeBack.CBG_TOTAL,
                            fmt=hcpsdk.mapi.ChargeBack.CBM_JSON
                            )

        print()
        print(type(l))
        pprint(json.load(l), indent=4)

        self.assertTrue(type(l) == StringIO)

    def test_1_20_chargeback_tenant_totals_xml(self):
        """
        Check if we can load all Tenants totals
        """
        print('test_1_20_chargeback_tenant_totals_xml:')

        l = self.cb.request(tenant='m', start=datetime.now()-timedelta(days=10),
                            end=datetime.now(),
                            granularity=hcpsdk.mapi.ChargeBack.CBG_TOTAL,
                            fmt=hcpsdk.mapi.ChargeBack.CBM_XML
                            )

        print()
        print(type(l))
        pprint(l.read(), indent=4)

        self.assertTrue(type(l) == StringIO)

    def test_1_30_chargeback_tenant_totals_csv(self):
        """
        Check if we can load all Tenants totals
        """
        print('test_1_30_chargeback_tenant_totals_csv:')

        l = self.cb.request(tenant='m', start=datetime.now()-timedelta(days=10),
                            end=datetime.now(),
                            granularity=hcpsdk.mapi.ChargeBack.CBG_TOTAL,
                            fmt=hcpsdk.mapi.ChargeBack.CBM_CSV
                            )

        print()
        print(type(l))
        pprint(l.read(), indent=4)

        self.assertTrue(type(l) == StringIO)
