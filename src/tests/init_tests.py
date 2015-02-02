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

import hcpsdk

# primary HCP
P_HCP       = 'hcp.snomis.local'
P_TENANT    = 'm.' + P_HCP
P_NS_GOOD   = 'n1.' + P_TENANT
P_NS_BAD    = "this_wont_work.at-all"
P_PORT      = 443
P_DNSCACHE  = True

P_USER      = "n"
P_PASSWORD  = "n01"
P_AUTH      = hcpsdk.NativeAuthorization(P_USER, P_PASSWORD)

# replica HCP
R_HCP       = 'hcp2.snomis.local'
R_TENANT    = 'm.' + R_HCP
R_NS_GOOD   = 'n1.' + R_TENANT
R_NS_BAD    = "this_wont_work.at-all"
R_PORT      = 443

R_USER      = P_USER
R_PASSWORD  = P_PASSWORD
R_AUTH      = hcpsdk.NativeAuthorization(R_USER, R_PASSWORD)
