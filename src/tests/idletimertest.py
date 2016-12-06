import sys
from os.path import join, normpath
import concurrent.futures
import time
import pprint
import hcpsdk

T_NAMESPACE = 'n1.m.hcp73.archivas.com'
T_DAAC      = 'n'
T_DAAC_PWD  = 'n01'
T_PORT      = 443
T_DEBUG     = True

T_THREADS        = 1          # no. of threads to use in parallel
T_OBJ            = 128            # the object we will use in a run (from objs)
T_CNT_PER_THREAD = 10          # how often the object will be written
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


def t_write(connection, tgtpath, buffer):
    '''
    Write a set of objects
    :param connection: the http connection to be used
    :param tgtpaths: a list of target paths
    :param buffer: the bytesarray holding the object
    :return: (overall service tme, no. of objs processed)
    '''
    try:
        r = connection.PUT(tgtpath, buffer)
    except Exception as e:
        print('Exception: {}'.format(str(e)))
    else:
        connection.read()

    return

def t_read(connection, tgtpath):
    '''
    Read a set of objects
    :param buffer: the bytesarray holding the object
    :param connection: the http connection to be used
    :param tgtpaths: a list of target paths
    :return: (overall service tme, no. of objs processed)
    '''
    try:
        r = connection.GET(tgtpath)
    except Exception as e:
        print('Exception: {}'.format(str(e)))
    else:
        connection.read()

    return

def t_delete(connection, tgtpath):
    '''
    Delete a set of objects
    :param buffer: the bytesarray holding the object
    :param connection: the http connection to be used
    :param tgtpaths: a list of target paths
    :return: (overall service tme, no. of objs processed)
    '''
    try:
        r = connection.DELETE(tgtpath)
    except Exception as e:
        print('Exception: {}'.format(str(e)))
    else:
        connection.read()

    return



if __name__ == '__main__':
    if T_DEBUG:
        import logging
        logging.basicConfig(level=logging.DEBUG, style='{', format='{levelname:>5s} {msg}')
        # noinspection PyShadowingBuiltins
        print = pprint = logging.info

    # the place where we will find the needed source objects
    if sys.platform == 'win32':
        T_INPATH = 'd:\\__files'
    elif sys.platform == 'darwin':
        T_INPATH = '/Volumes/dev/__files'
    else:
        sys.exit('source path is undefined')

    print("--> Init <hcptarget> object")
    try:
        auth = hcpsdk.NativeAuthorization(T_DAAC, T_DAAC_PWD)
        hcptarget = hcpsdk.Target(T_NAMESPACE, auth, T_PORT)
    except hcpsdk.HcpsdkError as e:
        sys.exit("Fatal: {}".format(e.errText))

    print("--> Init {} <connection> object(s)".format(T_THREADS))
    conns = None
    conntimes = 0.0
    outer_contime = time.time()
    try:
        conns = hcpsdk.Connection(hcptarget, debuglevel=0, idletime=3)
    except Exception as e:
        sys.exit('Exception: {}'.format(str(e)))
    else:
        conntimes += conns.connect_time
    outer_contime = time.time() - outer_contime

    print('\tinner connection time: {:,.5f}'.format(conntimes))
    print('\touter connection time: {:,.5f}'.format(outer_contime))

    # load one of the files into memory
    print('--> Loading test object into memory...')
    with open(join(T_INPATH,T_OBJS[T_OBJ]), 'rb') as inHdl:
        buf = bytearray(inHdl.read())
        size = len(buf)
        print('...object size = {}'.format(size))

    # Create the output paths
    outpath = join(T_STARTPATH, 'xxxxx')

    # now write the objects...
    #-------------------------
    print('--> Now ingesting objects:')
    outer_contime = time.time()
    try:
        t_write(conns, outpath, buf)
        print('PUT status: {}'.format(conns._response.status))
    except Exception as exc:
        print('PUT generated an exception: {}'.format(exc))
    outer_contime = time.time() - outer_contime
    print('\tinner service time:  {:,.5f} ({:5,.2f} Mb/sec)'.format(conns.service_time2,
                                                                    size/conns.service_time2/1024/1024))
    print('\touter service time:  {:,.5f} ({:5,.2f} Mb/sec)'.format(outer_contime, size/outer_contime/1024/1024))

    print('sleeping 10 secs')
    time.sleep(10)

    # now reading the objects...
    #---------------------------
    print('--> Now reading objects:')
    outer_contime = time.time()
    try:
        t_read(conns, outpath)
        print('GET status: {}'.format(conns._response.status))
    except Exception as exc:
        print('GET generated an exception: {}'.format('...', exc))
    outer_contime = time.time() - outer_contime
    print('\tinner service time:  {:,.5f} ({:5,.2f} Mb/sec)'.format(conns.service_time2,
                                                                    size/conns.service_time2/1024/1024))
    print('\touter service time:  {:,.5f} ({:5,.2f} Mb/sec)'.format(outer_contime, size/outer_contime/1024/1024))

    # now deleting objects...
    print('--> Now deleting objects:')
    outer_contime = time.time()
    try:
        t_delete(conns, outpath)
        print('DELETE status: {}'.format(conns._response.status))
    except Exception as exc:
        print('DELETE generated an exception: {}'.format('...', exc))
    outer_contime = time.time() - outer_contime
    print('\tinner service time:  {:,.5f} ({:5,.2f} Mb/sec)'.format(conns.service_time2,
                                                                    size/conns.service_time2/1024/1024))
    print('\touter service time:  {:,.5f} ({:5,.2f} Mb/sec)'.format(outer_contime, size/outer_contime/1024/1024))


    # close the session
    conns.close()
