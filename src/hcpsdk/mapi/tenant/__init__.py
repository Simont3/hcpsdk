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

import logging
from json import loads
import hcpsdk


__all__ = ['TenantError', 'tenants', 'Tenant']

logging.getLogger('hcpsdk.mapi.tenant').addHandler(logging.NullHandler())


class TenantError(Exception):
    """
    Base Exception used by the *hcpsdk.mapi.Tenant()* class.
    """
    def __init__(self, reason):
        """
        :param reason: An error description
        """
        self.args = (reason,)


def tenants(target, debuglevel=0):
    """
    Gets a list of existing Tenants within an *hcpsdk.Target* object

    :param target:      an hcpsdk.Target object
    :param debuglevel:  0..9 (used in *http.client*)
    :returns:           a list of *hcpsdk.Tenant* objects
    :raises:            *hcpsdk.HcpsdkPortError* in case *target* is
                        initialized with an incorrect port for use by
                        this class.
    """
    logger = logging.getLogger(__name__ + '.tenants')
    hcpsdk.checkport(target, hcpsdk.P_MAPI)

    try:
        con = hcpsdk.Connection(target, debuglevel=debuglevel)
    except Exception as e:
        raise hcpsdk.HcpsdkError(str(e))

    try:
        con.GET('/mapi/tenants', headers={'Accept': 'application/json'})
    except Exception as e:
        raise TenantError('list all Tenants failed: {}'.format(e))
    else:
        if con.response_status == 200:
            tl = []
            for t in loads(con.read().decode())['name']:
                print(t)
                tl.append(Tenant(target, t, debuglevel=debuglevel))
            return tl
        else:
            raise TenantError('unable to list Tenants ({} - {}'
                              .format(con.response_status, con.response_reason))


class Tenant(object):
    """
    Access to Tenant resources
    """

    def __init__(self, target, name, debuglevel=0):
        """
        :param target:      an hcpsdk.Target object
        :param name:        the Tenants name
        :param debuglevel:  0..9 (used in *http.client*)
        :raises:            *hcpsdk.HcpsdkPortError* in case *target* is
                            initialized with an incorrect port for use by
                            this class.
        """
        self.logger = logging.getLogger(__name__ + '.Tenant')
        hcpsdk.checkport(target, hcpsdk.P_MAPI)
        self.target = target
        self.debuglevel = debuglevel
        self.connect_time = 0.0
        self.service_time = 0.0
        self.prepare_xml = None
        self.suggestedfilename = '' # the filename suggested by HCP

        try:
            self.con = hcpsdk.Connection(self.target, debuglevel=self.debuglevel)
        except Exception as e:
            raise hcpsdk.HcpsdkError(str(e))

