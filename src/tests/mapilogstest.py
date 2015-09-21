
import sys
from pprint import pprint
import time
import logging
import cmd
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

    def do_what(self, arg):
        'what - print what will be downloaded'
        print('selected nodes:  {}'.format(self.nodes or 'all'))
        print('selected snodes: {}'.format(self.snodes or 'all'))
        print('selected logs:   {}'.format(self.logs or 'all'))

    def do_status(self, arg):
        'status - query the log preparation state on HCP'
        log.debug('do_status() called')
        pprint(l.status())
        print()

    def do_prepare(self, arg):
        'prepare - start log preparation on HCP'
        try:
            l.prepare(snodes=self.snodes)
        except Exception as e:
            print('prepare: LogsInProgessError: {}'.format(e))
        else:
            print('prepare initiated')
        print()

    def do_nodes(self, arg):
        'nodes [node_id,]* - select the nodes to download logs from\n'\
        '                    nothing selects all nodes'
        if arg:
            self.nodes = arg.split(',')
        else:
            self.nodes = []

    def do_snodes(self, arg):
        'snodes [snode_name,]* - select the S-nodes to download logs from\n'\
        '                        nothing selects all nodes'
        if arg:
            self.snodes = arg.split(',')
        else:
            self.snodes = []

    def do_logs(self, arg):
        'logs ([ACCESS|SYSTEM|SERVICE|APPLICATION],)* - select log types\n'\
        '                                               nothing selects all'
        if arg:
            self.logs = arg.split(',')
        else:
            self.logs = []


    def do_download(self, filename, ):
        'download <filename> - donwload logs and store into file <filename>'
        if not filename:
            print('Error: filename missing!')
            return

        print('downloading for nodes: {}\n'
              '               snodes: {}\n'
              '                 logs: {}\n'
              .format(self.nodes or 'all',
                      self.snodes or 'all (or none, if there are none)',
                      self.logs or 'all'))
        try:
            with open(filename, 'w+b') as outhdl:
                l.download(hdl=outhdl, nodes=self.nodes, snodes=self.snodes,
                           logs=self.logs, progresshook=showdownloadprogress)
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
        print()

    def do_test(self, args):
        print(args)

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
        return self.onecmd('status')
        # if self.lastcmd in ['status']:
        #     return self.onecmd(self.lastcmd)
        # else:
        #     print('no-op')

    def close(self):
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
    t = hcpsdk.Target(TGT, auth, port=PORT)
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
