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

# start sample block 10

import sys
from os.path import normpath
from pprint import pprint
import hcpsdk

# HCP connection details - you'll need to adopt this!
# -- primary HCP
P_FQDN = 'n1.m.hcp1.snomis.local'
P_USER = 'n'
P_PASS = 'n01'
P_PORT = 443
# -- file to be used for the test (read-only)
P_FILE = normpath('../testfiles/128kbfile')
# -- debug mode
P_DEBUG = False

if __name__ == '__main__':
    # end sample block 10
    # start sample block 15
    if P_DEBUG:
        import logging
        logging.basicConfig(level=logging.DEBUG, style='{', format='{levelname:>5s} {msg}')
        print = pprint = logging.info
    # end sample block 15
    # noinspection PyUnboundLocalVariable
    print('running *simple_primary_only.py*')

    # start sample block 20
    # Setup the target HCP objects:
    try:
        t = hcpsdk.target(P_FQDN, P_USER, P_PASS, port=P_PORT)
    except hcpsdk.HcpsdkError as e:
        sys.exit('init of *target* failed - {}'.format(e))
    else:
        print('target *t* was initialized with IP addresses: {}'.format(t.addresses))
    # end sample block 20

    # start sample block 30
    # setup a connection object:
    try:
        c = hcpsdk.connection(t)
    except hcpsdk.HcpsdkError as e:
        sys.exit('init of *target* failed - {}'.format(e))
    else:
        print('connection *c* uses IP address: {}'.format(c.address))
        print('')
        # end sample block 30

        # start sample block 40
        # ingest an object:
        try:
            with open(P_FILE, 'r') as infile:
                r = c.PUT('/rest/hcpsdk/sample_primary_only.txt',
                          body=infile,
                          params={'index': 'true', 'shred': 'true'})
        except hcpsdk.HcpsdkTimeoutError as e:
            sys.exit('PUT timed out - {}'.format(e))
        except hcpsdk.HcpsdkError as e:
            sys.exit('PUT failed - {}'.format(e))
        except OSError as e:
            sys.exit('failure on {} - {}'.format(P_FILE, e))
        else:
            if c.response_status == 201:
                print('PUT request was successful')
                print('used IP address: {}'.format(c.address))
                print('hash = {}'.format(c.getheader('X-HCP-Hash')))
                print('connect time:     {:0.12f} seconds'.format(c.connect_time))
                print('request duration: {:0.12f} seconds'.format(c.service_time2))
                print('')
            else:
                sys.exit('PUT failed - {}-{}'.format(c.response_status,
                                                     c.response_reason))
        # end sample block 40

        # start sample block 50
        # check an object for existence and get its metadata:
        try:
            r = c.HEAD('/rest/hcpsdk/sample_primary_only.txt')
        except hcpsdk.HcpsdkTimeoutError as e:
            sys.exit('HEAD timed out - {}'.format(e))
        except hcpsdk.HcpsdkError as e:
            sys.exit('HEAD failed - {}'.format(e))
        else:
            if c.response_status == 200:
                print('HEAD request was successful - headers:')
                pprint(c.getheaders())
                print('used IP address: {}'.format(c.address))
                print('request duration: {:0.12f} seconds'.format(c.service_time2))
                print('')
            else:
                sys.exit('HEAD failed - {}-{}'.format(c.response_status,
                                                      c.response_reason))
        # end sample block 50

        # start sample block 60
        # read an object:
        try:
            r = c.GET('/rest/hcpsdk/sample_primary_only.txt')
        except hcpsdk.HcpsdkTimeoutError as e:
            sys.exit('GET timed out - {}'.format(e))
        except hcpsdk.HcpsdkError as e:
            sys.exit('GET failed - {}'.format(e))
        else:
            if c.response_status == 200:

                print('GET request was successful - here\'s the content:')
                print('{}...'.format(c.read()[:40]))
                print('used IP address: {}'.format(c.address))
                print('request duration: {:0.12f} seconds'.format(c.service_time2))
                print('')
            else:
                sys.exit('GET failed - {}-{}'.format(c.response_status,
                                                     c.response_reason))
        # end sample block 60

        # start sample block 65
        # delete the object:
        try:
            r = c.DELETE('/rest/hcpsdk/sample_primary_only.txt')
        except hcpsdk.HcpsdkTimeoutError as e:
            sys.exit('DELETE timed out - {}'.format(e))
        except hcpsdk.HcpsdkError as e:
            sys.exit('DELETE failed - {}'.format(e))
        else:
            if c.response_status == 200:
                print('DELETE request was successful')
                print('used IP address: {}'.format(c.address))
                print('request duration: {:0.12f} seconds'.format(c.service_time2))
                print('')
            else:
                sys.exit('DELETE failed - {}-{}'.format(c.response_status,
                                                        c.response_reason))
                # end sample block 65

    # start sample block 70
    # close the connection:
    finally:
        # noinspection PyUnboundLocalVariable
        c.close()
        # end sample block 70
