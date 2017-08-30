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

import time

from datetime import date
import xml.etree.ElementTree as Et
from collections import OrderedDict
from tempfile import TemporaryFile, NamedTemporaryFile
import logging
import hcpsdk


__all__ = ['LogsError', 'LogsNotReadyError', 'LogsInProgessError', 'Logs']

logging.getLogger('hcpsdk.mapi.logs').addHandler(logging.NullHandler())


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
    L_ALL = [L_ACCESS, L_SYSTEM, L_SERVICE, L_APPLICATION]

    def __init__(self, target, debuglevel=0):
        """
        :param target:      an hcpsdk.Target object
        :param debuglevel:  0..9 (used in *http.client*)
        :raises:            *hcpsdk.HcpsdkPortError* in case *target* is
                            initialized with an incorrect port for use by
                            this class.
        """
        self.logger = logging.getLogger(__name__ + '.Logs')
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

    def mark(self, message):
        """
        Mark HCPs internal log with a message.

        :param message: the message to be logged
        :raises:        *LogsError*
        """
        if not message:
            raise LogsError('log message required')

        self.logger.debug('mark log with "{}"'.format(message))
        try:
            self.con.POST('/mapi/logs', params={'mark': message})
        except Exception as e:
            self.logger.error(e)
            raise LogsError(e)
        else:
            self.con.read()
            if self.con.response_status != 200:
                raise LogsError('{} - {} ({})'
                                .format(self.con.response_status,
                                        self.con.response_reason,
                                        self.con.getheader('X-HCP-ErrorMessage',
                                                                    default='?')))

    def prepare(self, startdate=None, enddate=None, snodes=[]):
        """
        Command HCP to prepare logs from *startdate* to *enddate* for
        later download.

        :param startdate:   1st day to collect (as a *datetime.date* object)
        :param enddate:     last day to collect (as a *datetime.date* object)
        :param snodes:      list of S-series nodes to collect from
        :returns:           a tuple of datetime.date(startdate),
                            datetime.date(enddate) and
                            str(prepared XML)
        :raises:            *ValueError* arguments are invalid or one of the
                            *LogsError* if an operation failed
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

        self.logger.debug('preparing logs for {} to {}'
                          .format(self.startdate.isoformat(),
                                  self.enddate.isoformat()))

        # Prepare the XML command file
        if snodes:
            xsnodes = '<snodes>' + ','.join(snodes) + '</snodes>'
        else:
            xsnodes = ''
        self.prepare_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' \
                           '<logPrepare>\n' \
                           '  <startDate>{:02}/{:02}/{:04}</startDate>\n' \
                           '  <endDate>{:02}/{:02}/{:04}</endDate>\n' \
                           '  {}\n' \
                           '</logPrepare>\n'\
                            .format(self.startdate.month, self.startdate.day,
                                    self.startdate.year, self.enddate.month,
                                    self.enddate.day, self.enddate.year,
                                    xsnodes)
        self.logger.debug('prepare_xml: {}'.format(self.prepare_xml))

        try:
            self.con.POST('/mapi/logs/prepare', body=self.prepare_xml,
                          headers={'Content-Type': 'application/xml'})
        except Exception as e:
            self.logger.error(e)
            raise LogsError(e)
        else:
            self.logger.debug('result: {} - {}'.format(self.con.response_status,
                                                       self.con.response_reason))
            self.logger.debug('returned headers: {}'.format(self.con.getheaders()))

            self.con.read()
            if self.con.response_status == 200:
                return(self.startdate, self.enddate, self.prepare_xml)
            elif self.con.response_status == 400:
                raise LogsInProgessError('{} - {} ({})'
                                         .format(self.con.response_status,
                                                 self.con.response_reason,
                                                 self.con.getheader('X-HCP-ErrorMessage',
                                                                    default='?')))
            else:
                raise LogsError('{} - {} ({})'
                                .format(self.con.response_status,
                                        self.con.response_reason,
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
        :raises:    re-raises whatever is raised below
        """
        self.logger.debug('status query issued')

        try:
            self.con.GET('/mapi/logs')
        except Exception as e:
            self.logger.error(e)
            raise
        else:
            self.logger.debug('response headers: {}'.format(self.con.getheaders()))
            xml = self.con.read().decode()
            time.sleep(.5)

            if self.con.response_status != 200:
                return None
            else:
                stat = OrderedDict()
                for child in Et.fromstringlist(xml):
                    if child.text == 'true':
                        stat[child.tag] = True
                    elif child.text == 'false':
                        stat[child.tag] = False
                    else:
                        stat[child.tag] = child.text.split(',')
                return stat

    def download(self, hdl=None, nodes=[], snodes=[], logs=[],
                 progresshook=None, hidden=True):
        """
        Download the requested logs.

        :param hdl:     a file (or file-like) handle open for binary
                        read/write or *None*, in which case a temporary file
                        will be created
        :param nodes:   list of node-IDs (int), all if empty
        :param snodes:  list of S-node names (str), none if empty
        :param logs:    list of logs (*L_**), all if empty
        :param progresshook:    a function taking a single argument (the #
                                of bytes received) that will be called after
                                each chunk of bytes downloaded
        :param hidden:  the temporary file created will be hidden if possible
                        (see `tempfile.TemporaryFile()
                        <https://docs.python.org/3/library/tempfile.html#tempfile.TemporaryFile>`_)
        :returns:       a 2-tuple: the file handle holding the received logs,
                        positioned at byte 0 and the filename suggested by
                        HCP
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

        # create the XML command structire
        str_nodes = str_snodes = str_logs = ''
        if nodes:
            str_nodes = '<nodes>' + ','.join(nodes) + '</nodes>'
        else:
            str_nodes = ''
        if snodes:
            str_snodes = ','.join(snodes)
        if logs:
            str_logs = ','.join(logs)
        else:
            str_logs = ','.join(Logs.L_ALL)

        xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' \
              '<logDownload>\n' \
              '    {}\n' \
              '    <snodes>{}</snodes>\n' \
              '    <content>{}</content>\n' \
              '</logDownload>'.format(str_nodes, str_snodes, str_logs).encode()

        self.logger.debug('dl_xml: {}'.format(xml))

        # download the logs
        try:
            self.con.POST('/mapi/logs/download', body=xml,
                          headers={'Accept': '*/*',
                                   'Content-Type': 'application/xml'})
        except Exception as e:
            self.logger.error(e)
            raise LogsError(e)
        else:
            self.logger.debug('result: {} - {}'.format(self.con.response_status,
                                                       self.con.response_reason))
            self.logger.debug('returned headers: {}'.format(self.con.getheaders()))
            suggestedfilename = self.con.getheader('Content-Disposition',
                                                   'name=no-name').split('=')[1]

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
                        break
            except Exception as e:
                raise LogsError(e)
        else:
            try:
                self.con.read()
            except Exception as e:
                raise LogsError(e)
            raise LogsError('{} - {} ({})'.format(self.con.response_status,
                                                  self.con.response_reason,
                                                  self.con.getheader('X-HCP-ErrorMessage',
                                                                     './.')))
        self.hdl.seek(0)
        return (self.hdl, suggestedfilename)

    def cancel(self):
        """
        Cancel a log request.

        :returns:   *True* if cancel was successfull
        :raises:    *LogsError* in case the cancel failed
        """
        self.logger.debug('cancel request issued')

        try:
            self.con.POST('/mapi/logs', params={'cancel': ''})
        except Exception as e:
            self.logger.error(e)
            raise LogsError(e)
        else:
            self.con.read() # cleanup

        if self.con.response_status == 200:
            self.suggestedfilename = ''
            return True
        else:
            self.logger.debug('{} - {} (cancel failed)'
                              .format(self.con.response_status,
                                    self.con.response_reason))
            raise LogsError('{} - {} (cancel failed)'
                            .format(self.con.response_status,
                                    self.con.response_reason))

    def close(self):
        """
        Close the underlying *hcpsdk.Connection()*.
        """
        self.logger.debug('close Logs()')
        self.suggestedfilename = ''
        self.con.close()


