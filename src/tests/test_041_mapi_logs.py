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
from datetime import date, timedelta
from collections import OrderedDict
import _io
import init_tests as it


class TestHcpsdk_41_1_Mapi_Logs(unittest.TestCase):
    def setUp(self):
        self.hcptarget = hcpsdk.Target(it.L_ADMIN, it.L_ADMAUTH,
                                       port=it.L_MAPIPORT, dnscache=it.L_DNSCACHE)
        self.logs = hcpsdk.mapi.Logs(self.hcptarget)

    def tearDown(self):
        self.logs.close()
        del self.hcptarget

    def test_1_05_logs_cancel(self):
        """
        Test if we get a dict from status()
        """
        print('test_1_05_logs_cancel:')
        self.assertTrue(self.logs.cancel() == True)

    def test_1_10_logs_prepare(self):
        """
        Test various good/bad parameters
        """
        print('test_1_10_logs_prepare:')

        l = self.logs.prepare()
        pprint(l, indent=4)
        self.assertTrue(l[0] == date(1970,1,1))
        self.assertTrue(l[1] == date.today())
        print('\tno date parameters: pass')

        l = self.logs.prepare(startdate=date.today() - timedelta(days=10),
                              enddate=date.today() - timedelta(days=1))
        pprint(l, indent=4)
        self.assertTrue(l[1] - l[0] == timedelta(days=9))
        print('\tpast 10 days: pass')

        with self.assertRaises(ValueError):
             l = self.logs.prepare(startdate='10/10/2014',
                                   enddate='12/31/2099')
        print('\t\tstartdate: pass')
        with self.assertRaises(ValueError):
             l = self.logs.prepare(startdate=date.today()-timedelta(days=10),
                                   enddate='12/31/2099')
        print('\t\tenddate: pass')
        with self.assertRaises(ValueError):
             l = self.logs.prepare(startdate=date.today()-timedelta(days=10),
                                   enddate=date.today() - timedelta(days=1),
                                   snodes=('s01','s02','s03'))
        print('\t\tsnodes: pass')
        print('\tfalse paramaters: pass')

    def test_1_20_logs_status(self):
        """
        Test if we get a dict from status()
        """
        print('test_1_20_logs_status:')
        l = self.logs.prepare(startdate=date.today()-timedelta(days=10),
                              enddate=date.today() - timedelta(days=1))
        stat = self.logs.status()
        pprint(stat, indent=4)
        self.assertTrue(type(stat) == OrderedDict)

    def test_1_30_logs_download(self):
        """
        Test if we fail when giving a none-file object to download
        """
        print('test_1_30_logs_download:')
        self.logs.prepare(startdate=date.today()-timedelta(days=10),
                          enddate=date.today() - timedelta(days=1))
        with self.assertRaises(hcpsdk.mapi.LogsError):
            fhdl = self.logs.download(5)
        print('\tinvalid file parameter: pass')

        #fhdl = self.logs.download()
        self.assertTrue(type(self.logs.download()) == _io.BufferedRandom)
        print('\tno file parameter: pass')

    def test_1_40_logs_cancel(self):
        """
        Test if we get a dict from status()
        """
        print('test_1_40_logs_cancel:')
        self.logs.prepare(startdate=date.today() - timedelta(days=10),
                              enddate=date.today() - timedelta(days=1))
        self.assertTrue(self.logs.cancel() == True)
