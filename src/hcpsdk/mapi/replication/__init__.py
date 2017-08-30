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

import xml.etree.ElementTree as Et
import logging
import hcpsdk


__all__ = ['ReplicationSettingsError', 'Replication']

logging.getLogger('hcpsdk.mapi.replication').addHandler(logging.NullHandler())


class ReplicationSettingsError(Exception):
    """
    Indicate an invalid action for the given link type (R_BEGINRECOVERY or
    R_COMPLETERECOVERY on a R_ACTIVE_ACTIVE link, R_FAILBACK on an
    R_OUTBOUND or R_INBOUND link).
    """

    def __init__(self, reason):
        """
        :param reason: An error description
        """
        self.args = (reason,)


class Replication(object):
    """
    Access replication link information, modify the replication link state.
    """
    # link types
    R_ACTIVE_ACTIVE = 'ACTIVE_ACTIVE'
    R_OUTBOUND = 'OUTBOUND'
    R_INBOUND = 'INBOUND'
    # link activity
    R_SUSPEND = 'suspend'  # suspend a link
    R_RESUME = 'resume'  # resume a link
    R_RESTORE = 'restore'  # restore a link
    R_FAILOVER = 'failOver'  # for all link types
    R_FAILBACK = 'failBack'  # for active/active links
    R_BEGINRECOVERY = 'beginRecovery'  # for active/passive links
    R_COMPLETERECOVERY = 'completeRecovery'  # dito

    def __init__(self, target, debuglevel=0):
        """
        :param target:      an hcpsdk.Target object
        :param debuglevel:  0..9 (used in *http.client*)
        """
        self.logger = logging.getLogger(__name__ + '.Replication')
        hcpsdk.checkport(target, hcpsdk.P_MAPI)
        self.target = target
        self.debuglevel = debuglevel
        self.connect_time = 0.0
        self.service_time = 0.0

    def getreplicationsettings(self):
        """
        Query MAPI for the general settings of the replication service.

        :return: a dict containing the settings
        :raises: HcpsdkError
        """
        d = {}
        try:
            con = hcpsdk.Connection(self.target, debuglevel=self.debuglevel)
        except Exception as e:
            raise hcpsdk.HcpsdkError(str(e))
        else:
            self.connect_time = con.connect_time
            try:
                r = con.GET('/mapi/services/replication')
            except Exception as e:
                raise hcpsdk.HcpsdkError(str(e))
            else:
                if r.status == 200:
                    # Good status, get and parse the Response
                    x = r.read()
                    self.service_time = con.service_time2
                    for child in Et.fromstring(x):
                        d[child.tag] = child.text
                else:
                    raise (hcpsdk.HcpsdkError('{} - {}'.format(r.status, r.reason)))
        finally:
            # noinspection PyUnboundLocalVariable
            con.close()

        return d

    def getlinklist(self):
        """
        Query MAPI for a list of replication links.

        :return:  a list with the names of replication links
        :raises: HcpsdkError
        """
        d = []
        try:
            con = hcpsdk.Connection(self.target, debuglevel=self.debuglevel)
        except Exception as e:
            raise hcpsdk.HcpsdkError(str(e))
        else:
            self.connect_time = con.connect_time
            try:
                r = con.GET('/mapi/services/replication/links')
            except Exception as e:
                d.append('Error: {}'.format(str(e)))
            else:
                if r.status == 200:
                    # Good status, get and parse the Response
                    x = r.read()
                    self.service_time = con.service_time2
                    root = Et.fromstring(x)
                    for child in root:
                        if child.tag == 'name':
                            d.append(child.text)
                else:
                    raise (hcpsdk.HcpsdkError('{} - {}'.format(r.status, r.reason)))
        finally:
            # noinspection PyUnboundLocalVariable
            con.close()

        return d

    def getlinkdetails(self, link):
        """
        Query MAPI for the details of a replication link.

        :param link:    the name of the link as retrieved by **getlinklist()**
        :return:        a dict holding the details
        :raises:        HcpsdkError
        """
        d = {}
        try:
            con = hcpsdk.Connection(self.target, debuglevel=self.debuglevel)
        except Exception as e:
            raise hcpsdk.HcpsdkError(str(e))
        else:
            self.connect_time = con.connect_time
            try:
                r = con.GET('/mapi/services/replication/links/{}'.format(link),
                            params={'verbose': 'true'})
            except Exception as e:
                raise hcpsdk.HcpsdkError(str(e))
            else:
                if r.status == 200:
                    # Good status, get and parse the Response
                    x = r.read()
                    self.service_time = con.service_time2
                    for child in Et.fromstring(x):
                        if child.text:
                            d[child.tag] = child.text
                        else:
                            d[child.tag] = {}
                            for i in child:
                                if i.text:
                                    d[child.tag][i.tag] = i.text
                                else:
                                    d[child.tag][i.tag] = {}
                                    for j in i:
                                        d[child.tag][i.tag][j.tag] = j.text
                else:
                    raise (hcpsdk.HcpsdkError('{} - {}'.format(r.status, r.reason)))
        finally:
            # noinspection PyUnboundLocalVariable
            con.close()

        return d

    def setreplicationlinkstate(self, linkname, action, linktype=None):
        """
        Alter the state of a replication link.

        :param linkname:    name of the link to change the state
        :param linktype:    one of ``[R_ACTIVE_ACTIVE, R_OUTBOUND, R_INBOUND]``;
                            not required for ``[R_SUSPEND, R_RESUME, R_RESTORE]``
        :param action:     one of ``[R_SUSPEND, R_RESUME, R_RESTORE, R_FAILOVER,
                            R_FAILBACK, R_BEGINRECOVERY, R_COMPLETERECOVERY]``
        :raises: HcpsdkError
        """
        # make sure that only valid linktypes and actions are accepted
        if linktype not in [Replication.R_ACTIVE_ACTIVE, Replication.R_OUTBOUND, Replication.R_INBOUND, None] or \
                        action not in [Replication.R_SUSPEND, Replication.R_RESUME,
                                       Replication.R_RESTORE, Replication.R_BEGINRECOVERY,
                                       Replication.R_COMPLETERECOVERY,
                                       Replication.R_FAILBACK, Replication.R_FAILOVER]:
            raise ValueError
        # make sure that no invalid action is called
        if (action == Replication.R_FAILBACK and linktype in [Replication.R_OUTBOUND, Replication.R_INBOUND]) or \
                (action in [Replication.R_BEGINRECOVERY, Replication.R_COMPLETERECOVERY] and
                         linktype == Replication.R_ACTIVE_ACTIVE) or \
                (action in [Replication.R_FAILOVER, Replication.R_FAILBACK,
                            Replication.R_BEGINRECOVERY, Replication.R_COMPLETERECOVERY] and not linktype):
            raise ReplicationSettingsError('{} not allowed on {} link'.format(action, linktype))

        # build params
        action = {action: ''}
        # let's do it!
        try:
            con = hcpsdk.Connection(self.target, debuglevel=self.debuglevel)
        except Exception as e:
            raise hcpsdk.HcpsdkError(str(e))
        else:
            try:
                r = con.POST('/mapi/services/replication/links/{}'
                             .format(linkname), params=action)
            except Exception as e:
                raise hcpsdk.HcpsdkError(str(e))
            else:
                if r.status != 200:
                    err = r.getheader('X-HCP-ErrorMessage', 'no message')
                    raise (hcpsdk.HcpsdkError('{} - {} ({})'.format(r.status, r.reason, err)))
                else:
                    r.read()
        finally:
            # noinspection PyUnboundLocalVariable
            con.close()


