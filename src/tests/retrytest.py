import sys
from os.path import join, normpath
import logging
import threading
import time
import pprint
import hcpsdk

T_NAMESPACE = 'n1.m.hcp73.archivas.com'
T_DAAC      = 'n'
T_DAAC_PWD  = 'n01'
T_PORT      = 443

T_THREADS        = 10          # no. of threads to use in parallel
T_OBJ            = 128            # the object we will use in a run (from objs)
T_CNT_PER_THREAD = 100          # how often the object will be written
T_OUTNAME   = '_hcp_loadtest'   # filename to be used
T_STARTPATH = '/rest/_hcp_loadtest/'    # path to write to

# a names of the source objects
T_OBJS = {     1: '1kbfile',
               8: '8kbfile',
              16: '16kbfile',
              32: '32kbfile',
              64: '64kbfile',
             128: '128kbfile',
             256: '256kbfile',
             512: '512kbfile',
            1024: '1mbfile',
           10240: '10mbfile',
          102400: '100mbfile'}



if __name__ == '__main__':
    strhandler = logging.StreamHandler(sys.stdout)
    frm = logging.Formatter("\t%(asctime)s [%(levelname)-8s] %(threadName)s:%(name)s.%(funcName)s.%(lineno)d: %(message)s") #, "%m/%d %H:%M:%S")
    l = logging.getLogger()
    strhandler.setFormatter(frm)
    l.addHandler(strhandler)
#    l.setLevel(logging.WARNING)
    l.setLevel(logging.DEBUG)

    # the place where we will find the needed source objects
    if sys.platform == 'win32':
        T_INPATH = 'd:\\__files'
    elif sys.platform == 'darwin':
        T_INPATH = '/Volumes/dev/__files'
    else:
        sys.exit('source path is undefined')

    # the paths in which we will store the objects
    i1 = normpath(join(T_STARTPATH, T_OUTNAME, '1')).replace('\\', '/')
    i2 = normpath(join(T_STARTPATH, T_OUTNAME, '2')).replace('\\', '/')

    # load one of the files into memory
    print('--> Loading test object into memory - ', end='')
    with open(join(T_INPATH,T_OBJS[T_OBJ]), 'rb') as inHdl:
        buf = bytearray(inHdl.read())
        size = len(buf)
        print('object size = {}'.format(size))

    print("--> Init <hcpsdk.target> object")
    try:
        hcptarget = hcpsdk.target(T_NAMESPACE, T_DAAC, T_DAAC_PWD, T_PORT)
    except hcpsdk.HcpsdkError as e:
        sys.exit("Fatal: {}".format(e.errText))

    print("--> Init <hcpsdk.connection> object")
    try:
        con = hcpsdk.connection(hcptarget, idletime=3, debuglevel=9)
    except Exception as e:
        sys.exit('Exception: {}'.format(str(e)))

    print("--> Write 1st file:", i1)
    try:
        r = con.PUT(i1, buf)
        print(r.status)
    except Exception as e:
        print('Exception: {}'.format(str(e)))

    secs = 10
    print("--> sleep for {}".format(secs))
    time.sleep(secs)

    print("--> Write 2nd file:", i2)
    try:
        r = con.PUT(i2, buf)
        print(r.status)
    except Exception as e:
        print('Exception: {}'.format(str(e)))

    print("--> HEAD 1st file:", i1)
    try:
        r = con.HEAD(i1)
        print(r.status)
    except Exception as e:
        print('Exception: {}'.format(str(e)))

    print("--> HEAD 2nd file:", i2)
    try:
        r = con.HEAD(i2)
        print(r.status)
    except Exception as e:
        print('Exception: {}'.format(str(e)))

    print("--> Set indexing on 1st file:", i1)
    try:
        r = con.POST(i1, ['index=true'])
        print(r.status)
    except Exception as e:
        print('Exception: {}'.format(str(e)))

    print("--> Set indexing on 2nd file:", i2)
    try:
        r = con.POST(i2, ['index=true'])
        print(r.status)
    except Exception as e:
        print('Exception: {}'.format(str(e)))

    print("--> Read 1st file:", i1)
    try:
        r = con.GET(i1)
        print(r.status)
    except Exception as e:
        print('Exception: {}'.format(str(e)))
    else:
        con.read()

    print("--> Read 2nd file:", i2)
    try:
        r = con.GET(i2)
        print(r.status)
    except Exception as e:
        print('Exception: {}'.format(str(e)))
    else:
        con.read()

    print("--> Delete 1st file:", i1)
    try:
        r = con.DELETE(i1)
        print(r.status)
    except Exception as e:
        print('Exception: {}'.format(str(e)))

    print("--> Delete 2nd file:", i2)
    try:
        r = con.DELETE(i2)
        print(r.status)
    except Exception as e:
        print('Exception: {}'.format(str(e)))

    print("--> Close <hcpsdk.connection> object")
    con.close()

    while True:
        ts = threading.active_count()
        l.info('--> Threads: {}'.format(ts))
        if ts == 1:
            break
        time.sleep(1)
