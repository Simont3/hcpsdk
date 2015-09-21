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

# for debug purposes
import sys
import time

from datetime import date
import xml.etree.ElementTree as Et
from collections import OrderedDict
from tempfile import TemporaryFile, NamedTemporaryFile
import _io # needed to check type of file parameter in Logs.download()
import logging
from pprint import pprint

import hcpsdk


__all__ = ['Logs', 'ReplicationSettingsError', 'Replication']

logging.getLogger('hcpsdk.mapi').addHandler(logging.NullHandler())


class LogsError(Exception):
    """
    Base Exception used by the *hcpsdk.mapi.Logs()* class.
    """
    def __init__(self, reason):
        """
        :param reason: An error description
        """
        self.args = (reason,)

class LogsNotReadyError(LogsError):
    """
    Raised by *Logs.download()* in case there are no logs ready to be
    downloaded.
    """
    def __init__(self, reason):
        """
        :param reason: An error description
        """
        self.args = (reason,)

class LogsInProgessError(LogsError):
    """
    Raised by *Logs.download()* in case the log download is already
    in progress.
    """
    def __init__(self, reason):
        """
        :param reason: An error description
        """
        self.args = (reason,)


class Logs(object):
    """
    Access to HCP internal logfiles (ACCESS, SYSTEM, SERVICE, APPLICATION)
    """

    L_ACCESS = 'ACCESS' # http access logs
    L_SYSTEM = 'SYSTEM' #
    L_SERVICE = 'SERVICE' #
    L_APPLICATION = 'APPLICATION' #

    def __init__(self, target, debuglevel=0):
        """
        :param target:      an hcpsdk.Target object
        :param debuglevel:  0..9 (used in *http.client*)
        :raises:            *hcpsdk.HcpsdkPortError* in case *target* is
                            initialized with an incorrect port for use by
                            this class.
        """
        hcpsdk.checkport(target, hcpsdk.P_MAPI)
        self.target = target
        self.debuglevel = debuglevel
        self.connect_time = 0.0
        self.service_time = 0.0
        self.logger = logging.getLogger('hcpsdk.mapi.Logs')
        self.prepare_xml = None

        try:
            self.con = hcpsdk.Connection(self.target, debuglevel=self.debuglevel)
        except Exception as e:
            raise hcpsdk.HcpsdkError(str(e))


    def prepare(self, startdate=None, enddate=None, snodes=[]):
        """
        Command HCP to prepare logs from *startdate* to *enddate* for
        later download.

        :param startdate:   1st day to collect (as a *datetime.date* object)
        :param enddate:     last day to collect (as a *datetime.date* object)
        :param snodes:      list of S-series nodes to collect from
        :returns:           (datetime.date(startdate), datetime.date(enddate),
                            str(prepared XML))
        :raises:            *ValueError* or one of the
        """
        if startdate and type(startdate) != date:
            raise ValueError('startdate not of type(datetime.date)')
        else:
            self.startdate = startdate or date(1970,1,1)
        if enddate and type(enddate) != date:
            raise ValueError('enddate not of type(datetime.date)')
        else:
            self.enddate = enddate or date.today()
        if type(snodes) != list:
            raise ValueError('snodes not of type(list)')

        self.logger.debug('preparing logs for {}/{}/{} to {}/{}/{}'
                          .format(self.startdate.year, self.startdate.month,
                                  self.startdate.day, self.enddate.year,
                                  self.enddate.month, self.enddate.day))

        # Prepare the XML command file
        self.prepare_xml = '<logPrepare>\n' \
                           '  <startDate>{:02}/{:02}/{:04}</startDate>\n' \
                           '  <endDate>{:02}/{:02}/{:04}</endDate>\n' \
                           '  <snodes>{}</snodes>\n' \
                           '</logPrepare>\n'\
                            .format(self.startdate.month, self.startdate.day,
                                    self.startdate.year, self.enddate.month,
                                    self.enddate.day, self.enddate.year,
                                    ','.join(snodes))

        try:
            self.con.POST('/mapi/logs/prepare', body=self.prepare_xml)
        except Exception as e:
            self.logger.error(e)
            raise LogsError(e)
        else:
            self.con.read()
            if self.con.response_status == 200:
                return(self.startdate, self.enddate, self.prepare_xml)
            elif self.con.response_status == 400:
                    # self.con.getheader('X-HCP-ErrorMessage', default='?')\
                    #         .startswith('A log download'):
                raise LogsInProgessError(self.con.getheader('X-HCP-ErrorMessage',
                                                            default='?'))
            else:
                raise LogsError('prepare failed ({} - {})'
                                .format(self.con.response_status,
                                        self.con.getheader('X-HCP-ErrorMessage',
                                                           default='?')))

    def status(self):
        """
        Query HCP for the status of the request log download.

        :returns:   a *collection.OrderedDict*:
                    ::

                        {
                         readyForStreaming: bool,
                         streamingInProgress: bool,
                         started: bool,
                         error: bool,
                         content: list # one or more of: L_ACCESS, L_SYSTEM,
                                       # L_SERVICE, L_APPLICATION)
                        }
        """
        self.logger.debug('status query issued')

        try:
            self.con.GET('/mapi/logs')
        except Exception as e:
            self.logger.error(e)
            print('error in status():', e, file=sys.stderr)
        else:
            self.logger.debug('response headers: {}'.format(self.con.getheaders()))
            xml = self.con.read().decode()
            # print(self.con.response_status, self.con.response_reason,
            #       file=sys.stderr)
            # pprint(self.con.getheaders(), stream=sys.stderr)
            # print('xml=', xml, file=sys.stderr)
            time.sleep(.5)

            if self.con.response_status != 200:
                return(None)
            else:
                stat = OrderedDict()
                for child in Et.fromstringlist(xml):
                    if child.text == 'true':
                        stat[child.tag] = True
                    elif child.text == 'false':
                        stat[child.tag] = False
                    else:
                        stat[child.tag] = child.text.split(',')

                # self.logger.debug(stat)

                return stat

    def download(self, hdl=None, nodes=[], snodes= [], logs=[],
                 progresshook=None, hidden=True):
        """
        Download the requested logs.

        :param hdl:     a file (or file-like) handle open for binary
                        read/write or *None*, in which case a temporary file
                        will be created
        :parm nodes:    list of node-IDs (int)
        :parm snodes:   list of S-node names (str)
        :param logs:    list of logs (*L_**)
        :param progresshook:    a function taking a single argument (the #
                                of bytes received) that will be called after
                                each chunk of bytes downloaded
        :param hidden:  the temporary file created will be hidden if possible
                        (see `tempfile.TemporaryFile()
                        <https://docs.python.org/3/library/tempfile.html#tempfile.TemporaryFile>`_)
        :returns:       the file handle holding the received logs,
                        positioned at byte 0.
        :raises:        *LogsError* or *LogsNotReadyError*
        """

        # make sure we have a file handle open for binary read/write
        if not hdl:
            if hidden:
                self.hdl = TemporaryFile('w+b')
            else:
                self.hdl = NamedTemporaryFile('w+b')
        else:
            self.hdl = hdl

        # check if the logs are ready for download
        if not self.status()['readyForStreaming']:
            raise LogsNotReadyError('not ready for streaming')

        # create the XML command structire
        str_nodes = str_snodes = str_logs = ''
        if nodes:
            str_nodes = ','.join(nodes)
        if snodes:
            str_snodes = ','.join(snodes)
        if logs:
            str_logs = ','.join(logs)

        xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' \
              '<logDownload>\n' \
              '    <nodes>{}</nodes>\n' \
              '    <snodes>{}</snodes>\n' \
              '    <content>{}</content>\n' \
              '</logDownload>'.format(str_nodes, str_snodes, str_logs).encode()

        self.logger.debug('dl_xml: {}'.format(xml))
        # download the logs
        try:
            self.con.POST('/mapi/logs/download', body=xml)
#                          headers={'Content-type': 'application/xml'})
        except Exception as e:
            self.logger.error(e)
            raise LogsError(e)
        else:
            self.logger.debug('returned headers: {}'.format(self.con.getheaders()))

        if self.con.response_status == 200:
            numbytes = 0
            try:
                while True:
                    d = self.con.read(amt=2**18)
                    numbytes += len(d)
                    if progresshook:
                        progresshook(numbytes)
                    if d:
                        self.hdl.write(d)
                    else:
                        print()
                        break
            except Exception as e:
                raise LogsError(e)

        self.hdl.seek(0)
        return self.hdl

    def cancel(self):
        """
        Cancel a log request.

        :returns:   *True* if cancel was successfull
        :raises:    *LogsError* in case the cancel failed
        """
        self.logger.debug('cancel log request issued')

        try:
            self.con.POST('/mapi/logs', params={'cancel': ''})
        except Exception as e:
            self.logger.error(e)
            raise LogsError(e)
        else:
            self.con.read() # cleanup

        if self.con.response_status == 200:
            pprint(self.con.getheaders())
            return True
        else:
            raise LogsError('cancel failed ({})'
                            .format(self.con.response_status))

    def close(self):
        """
        Close the used *hcpsdk.Connection()*.
        """
        self.con.close()





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
        hcpsdk.checkport(target, hcpsdk.P_MAPI)
        self.target = target
        self.debuglevel = debuglevel
        self.connect_time = 0.0
        self.service_time = 0.0
        self.logger = logging.getLogger('hcpsdk.mapi.Replication')

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
        Failover and  failback a replication link.

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


