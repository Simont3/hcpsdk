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

import logging
from json import loads
from pprint import pprint
import hcpsdk


__all__ = ['TenantError', 'listtenants', 'Tenant']

logging.getLogger('hcpsdk.mapi.tenant').addHandler(logging.NullHandler())


class TenantError(Exception):
    """
    Base Exception used by the *hcpsdk.mapi.Tenant()* class
    """
    def __init__(self, reason):
        """
        :param reason: An error description
        """
        self.args = (reason,)


def listtenants(target, timeout=60, debuglevel=0):
    """
    Get a list of available Tenants

    :param target:      an hcpsdk.Target object
    :param timeout:     the connection timeout in seconds
    :param debuglevel:  0..9 (used in *http.client*)
    :returns:           a list() of *Tenant()* objects
    :raises:            *hcpsdk.HcpsdkPortError* in case *target* is
                        initialized with a port different that *P_MAPI*
    """
    logger = logging.getLogger(__name__)
    logger.debug('getting a list of Tenants')
    hcpsdk.checkport(target, hcpsdk.P_MAPI)
    tenantslist = []

    try:
        con = hcpsdk.Connection(target, timeout=timeout, debuglevel=debuglevel)
    except Exception as e:
        raise hcpsdk.HcpsdkError(str(e))

    try:
        con.GET('/mapi/tenants', headers={'Accept': 'application/json'},
                params={'verbose': 'true'})
    except Exception as e:
        logger.debug('getting a list of Tenants failed: {}'.format(e))
        raise TenantError('get Tenant list failed: {}'.format(e))
    else:
        if con.response_status == 200:
            for t in loads(con.read().decode())['name']:
                tenantslist.append(Tenant(target, t, debuglevel=debuglevel))
            logger.debug('got a list of {} Tenants'.format(len(tenantslist)))
        else:
            con.close()
            logger.debug('getting a list of Tenants failed: {}-{}'
                         .format(con.response_status, con.response_reason))
            raise TenantError('unable to list Tenants ({} - {})'
                              .format(con.response_status,
                                      con.response_reason))

    con.close()
    return tenantslist



class Tenant(object):
    """
    A class representing a Tenant
    """

    # TODO: this object is simply a container for a single tenants settings
    #       remove all the other stuff...

    def __init__(self, target, name, timeout=60, debuglevel=0):
        """
        :param target:      an hcpsdk.Target object
        :param name:        the Tenants name
        :param timeout:     the connection timeout in seconds
        :param debuglevel:  0..9 (used in *http.client*)
        """
        self.logger = logging.getLogger(__name__ + '.Tenant')
        self.target = target
        try:
            self.con = hcpsdk.Connection(self.target, timeout=timeout,
                                         debuglevel=debuglevel)
        except Exception as e:
            raise hcpsdk.HcpsdkError(str(e))

        self.name = name        # the Tenants name
        self._settings = {}     # the Tenants base settings

        self.logger.debug('initialized for "{}"'.format(self.name))


    def info(self, cache=True):
        """
        Get the settings of the Tenant

        :param cache:   a bool indicating if cached information shall be used
        :return:        a dict holding the Tenants settings
        """

        if not self._settings or not cache:
            try:
                self.con.GET('/mapi/tenants/{}'.format(self.name),
                             headers={'Accept': 'application/json'})
            except Exception as e:
                raise hcpsdk.HcpsdkError(str(e))
            else:
                if self.con.response_status == 200:
                    self._settings = loads(self.con.read().decode())
                    self.logger.debug('got settings of Tenant {}'
                                      .format(self.name))
                else:
                    self.logger.debug('getting settings of Tenant {} '
                                      'failed: {}-{}'
                                      .format(self.con.response_status,
                                              self.con.response_reason))
                    raise TenantError('unable to list Tenants ({} - {})'
                                      .format(self.con.response_status,
                                              self.con.response_reason))
        return self._settings

    def close(self):
        """
        Close the underlying *hcpsdk.Connection()* object
        """
        self.con.close()
