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

from datetime import datetime, timedelta
from time import strftime
from io import StringIO
import logging
import hcpsdk


__all__ = ['ChargebackError', 'ChargeBack']

logging.getLogger('hcpsdk.mapi.chargeback').addHandler(logging.NullHandler())

class ChargebackError(Exception):
    """
    Base Exception used by the *hcpsdk.mapi.Chargeback()* class.
    """
    def __init__(self, reason):
        """
        :param reason: An error description
        """
        self.args = (reason,)


class ChargeBack(object):
    '''
    Access to HCP chargeback reports
    '''

    # the granularity modes allowed for chargeback collection
    CBG_DAY = 'day'
    CBG_HOUR = 'hour'
    CBG_TOTAL = 'total'
    CBG_ALL = [CBG_DAY, CBG_HOUR, CBG_TOTAL]

    # the output formats available
    CBM_CSV = 'text/csv'
    CBM_JSON = 'application/json'
    CBM_XML = 'application/xml'
    CBM_ALL = [CBM_CSV, CBM_JSON, CBM_XML]

    def __init__(self, target, debuglevel=9):
        '''
        :param target:      an hcpsdk.Target object
        :param debuglevel:  0..9 (used in *http.client*)
        '''
        self.logger = logging.getLogger(__name__ + '.Chargeback')
        hcpsdk.checkport(target, hcpsdk.P_MAPI)
        self.target = target
        self.debuglevel = debuglevel
        self.connect_time = 0.0
        self.service_time = 0.0

        try:
            self.con = hcpsdk.Connection(self.target, debuglevel=self.debuglevel)
        except Exception as e:
            raise hcpsdk.HcpsdkError(str(e))


    def request(self, tenant=None, start=None, end=None,
                granularity=CBG_TOTAL, fmt=CBM_JSON):
        '''
        Request a chargeback report for
        :param tenant:      the *Tenant* to collect from
        :param start:       starttime (a datetime object)
        :param end:         endtime (a datetime object)
        :param granularity: one out of CBG_ALL
        :param fmt:         output format, one out of CBM_ALL
        :return:            a StringIO object containing the report
        '''
        if not tenant:
            raise ValueError('no tenant given')
        else:
            self.tenant = tenant
        if start and type(start) != datetime:
            raise ValueError('start not of type(datetime.datetime)')
        else:
            self.start = start or datetime.now() - timedelta(days=180)
        if end and type(end) != datetime:
            raise ValueError('end not of type(datetime.datetime)')
        else:
            self.end = end or datetime.now()
        if granularity not in ChargeBack.CBG_ALL:
            raise ValueError('granularity not in {}'
                             .format(ChargeBack.CBG_ALL))
        else:
            self.granularity = granularity
        if fmt not in ChargeBack.CBM_ALL:
            raise ValueError('fmt not in {}'.format(ChargeBack.CBM_ALL))
        else:
            self.fmt = fmt

        self.logger.debug('request for {} ({} - {}), {}, {}'
                          .format(self.tenant,
                                  self.start.isoformat(),
                                  self.end.isoformat(),
                                  self.granularity, self.fmt))

        try:
            self.con.GET('/mapi/tenants/{}/chargebackReport'.format(self.tenant),
                         params={'start': self.start.strftime('%Y-%m-%dT%H:%M:%S')+strftime('%z'),
                                 'end': self.end.strftime('%Y-%m-%dT%H:%M:%S')+strftime('%z'),
                                 'granularity': self.granularity},
                         headers={'Accept': self.fmt})
        except Exception as e:
            self.logger.error(e)
            raise ChargebackError(e)
        else:
            self.logger.debug('result: {} - {}'.format(self.con.response_status,
                                                       self.con.response_reason))
            self.logger.debug('returned headers: {}'.format(self.con.getheaders()))

            if self.con.response_status == 200:
                return(self.con.read())
            else:
                raise ChargebackError('{} - {} ({})'
                                      .format(self.con.response_status,
                                              self.con.response_reason,
                                              self.con.getheader('X-HCP-ErrorMessage',
                                                                 default='?')))

    def close(self):
        '''
        Close the underlying *hcpsdk.Connection* object
        '''
        self.con.close()