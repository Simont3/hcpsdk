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

from hcpsdk.pathbuilder import PathBuilder


class TestHcpsdk_50_1_PathBuilder(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_1_10_buildpath(self):
        """
        Make sure we get a tuple containing a path and a UUID as string
        """
        print('test_1_10_buildpath:')
        b = PathBuilder()
        t = b.getunique('testfile.txt')
        print(t)
        self.assertTrue(type(t) == tuple)
        self.assertTrue(len(t) == 2)

    def test_1_20_buildpath_annotation(self):
        """
        Make sure we get a tuple containing a path and a UUID as string
        """
        print('test_1_20_buildpath_annotation:')
        b = PathBuilder(annotation=True)
        t = b.getunique('testfile.txt')
        print(t[0:2])
        for i in t[2].split(sep='\n'):
            print(i)
        self.assertTrue(type(t) == tuple)
        self.assertTrue(len(t) == 3)


if __name__ == '__main__':
    unittest.main()
