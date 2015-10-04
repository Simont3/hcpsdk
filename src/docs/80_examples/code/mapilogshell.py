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

import sys
from pprint import pprint
import logging
import cmd
from datetime import date, timedelta
import hcpsdk

USR = 'service'
PWD = 'service01'
TGT = 'admin.hcp72.archivas.com'
PORT = 9090


class LogsShell(cmd.Cmd):
    intro = 'HCP Log Download Shell.   Type help or ? to list commands.\n'
    prompt = '==> '

    def preloop(self):
        self.nodes = []
        self.snodes = []
        self.logs = []
        self.start = date.today() - timedelta(days=7)
        self.end = date.today()

    def do_what(self, arg):
        'what - show what is selected for download'
        print('start date:      {}'.format(self.start.strftime('%Y/%m/%d')))
        print('end date:        {}'.format(self.end.strftime('%Y/%m/%d')))

        print('selected nodes:  {}'.format(' '.join(self.nodes) or \
                                           ' '.join([x.split('.')[3]
                                                     for x in l.target.addresses])))
        print('selected snodes: {}'.format(' '.join(self.snodes) or 'none'))
        print('selected logs:   {}'.format(' '.join(self.logs) or \
                                           ' '.join(hcpsdk.mapi.Logs.L_ALL)))

    def do_status(self, arg):
        'status - query HCP for the log preparation status'
        log.debug('do_status() called')
        pprint(l.status())

    def do_prepare(self, arg):
        'prepare - trigger HCP to prepare the logs for later download'
        try:
            l.prepare(snodes=self.snodes, startdate=self.start,
                      enddate=self.end)
        except Exception as e:
            print('prepare failed: {}'.format(e))
        else:
            print('preparing for nodes: all\n'
                  '             snodes: {}\n'
                  '         date range: {} - {}'
                  .format(' '.join(self.snodes) or 'none',
                          self.start.strftime('%Y/%m/%d'),
                          self.end.strftime('%Y/%m/%d')))

    def do_nodes(self, arg):
        'nodes [node_id,]* - select the nodes to download logs from\n'\
        '                    (no argument selects all nodes)'
        if arg:
            self.nodes = []
            n = [x.split('.')[3] for x in l.target.addresses]
            for x in arg.split(','):
                if x in n:
                    self.nodes.append(x)
                else:
                    print('invalid: {}'.format(x))
        else:
            self.nodes = []

    def do_snodes(self, arg):
        'snodes [snode_name,]* - select the S-nodes to download logs from\n'\
        '                        (no argument disables S-Node log download)'
        if arg:
            self.snodes = arg.split(',')
        else:
            self.snodes = []

    def do_logs(self, arg):
        'logs [ACCESS,|SYSTEM,|SERVICE,|APPLICATION]* - select log types\n'\
        '                                               nothing selects all'
        if arg:
            self.logs = []
            for x in [y.upper() for y in arg.split(',')]:
                if x in hcpsdk.mapi.Logs.L_ALL:
                    self.logs.append(x)
                else:
                    print('invalid: {}'.format(x))
        else:
            self.logs = []

    def do_start(self, arg):
        'start YYYY/MM/DD - select start date (default is a week ago)'
        try:
            d = arg.split('/')
            self.start = date(int(d[0]),int(d[1]),int(d[2]))
        except Exception as e:
            print('invalid input - YYYY/MM/DD required...')

    def do_end(self, arg):
        'end YYYY/MM/DD - select end date (default is today)'
        try:
            d = arg.split('/')
            self.end = date(int(d[0]),int(d[1]),int(d[2]))
        except Exception as e:
            print('invalid input - YYYY/MM/DD required...')


    def do_download(self, filename, ):
        'download <filename> - donwload logs and store into file <filename>'
        if not filename:
            print('Error: filename missing!')
            return

        print('downloading for nodes: {}\n'
              '               snodes: {}\n'
              '                 logs: {}\n'
              '           date range: {} - {}\n'
              .format(' '.join(self.nodes) or \
                      ' '.join([x.split('.')[3] for x in l.target.addresses]),
                      ' '.join(self.snodes) or 'none',
                      ' '.join(self.logs) or \
                      ' '.join(hcpsdk.mapi.Logs.L_ALL,),
                      self.start.strftime('%Y/%m/%d'),
                      self.end.strftime('%Y/%m/%d')))
        try:
            with open(filename, 'w+b') as outhdl:
                hdl, n = l.download(hdl=outhdl, nodes=self.nodes,
                                    snodes=self.snodes, logs=self.logs,
                                    progresshook=showdownloadprogress)
                print('HCP suggested filename: {}'.format(n))
        except Exception as e:
            print('Error: {}'.format(e))
        else:
            print('download finished')

    def do_cancel(self, arg):
        'cancel - abort a log preparation'
        try:
            l.cancel()
        except Exception as e:
            print('cancel: {}'.format(e))
        else:
            print('cancel done')

    def do_mark(self, arg):
        'mark - mark HCPs log with a message'
        try:
            l.mark(arg)
        except Exception as e:
            print('mark failed: {}'.format(e))
        else:
            print('log marked')

    def do_quit(self, arg):
        'quit - exit the HCP Logs Shell'
        self.close()
        print('Bye...')
        return True

    def do_debug(self, arg):
        'debug - Toggle debug output'
        if log.getEffectiveLevel() != logging.DEBUG:
            log.setLevel(logging.DEBUG)
            log.debug('debug enabled')
            print('debug enabled')
        else:
            log.setLevel(logging.INFO)
            print('debug disabled')

    def emptyline(self):
        'run the status command if no command is given'
        return self.onecmd('status')

    def close(self):
        'close the underlying *hcpsdk.Logs()* object'
        l.close()


def showdownloadprogress(nBytes):
    '''
    Print a simple progress meter
    '''
    sz = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    i = 0
    while nBytes > 1023:
                    nBytes = nBytes / 1024
                    i = i + 1
    print("\rreceived: {0:.2f} {1:}".format(nBytes, sz[i]), end='')


if __name__ == '__main__':

    auth = hcpsdk.NativeAuthorization(USR,PWD)
    try:
        t = hcpsdk.Target(TGT, auth, port=PORT)
    except hcpsdk.ips.IpsError as e:
        sys.exit('Can\'t resolve "{}"\n\t==> {}'.format(TGT, e))
    l = hcpsdk.mapi.Logs(t, debuglevel=0)

    # create console handler with a higher log level
    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.DEBUG)
    fh = logging.Formatter("[%(levelname)-8s]: %(message)s")
    sh.setFormatter(fh)
    log = logging.getLogger()
    log.addHandler(sh)
    log.setLevel(logging.INFO)


    LogsShell().cmdloop()
