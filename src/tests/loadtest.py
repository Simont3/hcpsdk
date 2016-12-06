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


def t_write(connection, tgtpaths, buffer):
    '''
    Write a set of objects
    :param connection: the http connection to be used
    :param tgtpaths: a list of target paths
    :param buffer: the bytesarray holding the object
    :return: (overall service tme, no. of objs processed)
    '''
    sumtime = 0.0
    sumobjs = 0
    for i in tgtpaths:
        try:
            r = connection.request('PUT', i, buffer)
        except Exception as e:
            print('Exception: {}'.format(str(e)))
        else:
            connection.read()
            sumtime += connection.service_time2
            sumobjs += 1

    return(sumtime, sumobjs)

def t_read(connection, tgtpaths):
    '''
    Read a set of objects
    :param buffer: the bytesarray holding the object
    :param connection: the http connection to be used
    :param tgtpaths: a list of target paths
    :return: (overall service tme, no. of objs processed)
    '''
    sumtime = 0.0
    sumobjs = 0
    for i in tgtpaths:
        try:
            r = connection.request('GET', i)
        except Exception as e:
            print('Exception: {}'.format(str(e)))
        else:
            connection.read()
            sumtime += connection.service_time2
            sumobjs += 1

    return(sumtime, sumobjs)

def t_delete(connection, tgtpaths):
    '''
    Delete a set of objects
    :param buffer: the bytesarray holding the object
    :param connection: the http connection to be used
    :param tgtpaths: a list of target paths
    :return: (overall service tme, no. of objs processed)
    '''
    sumtime = 0.0
    sumobjs = 0
    for i in tgtpaths:
        try:
            r = connection.request('DELETE', i)
        except Exception as e:
            print('Exception: {}'.format(str(e)))
        else:
            connection.read()
            sumtime += connection.service_time2
            sumobjs += 1

    return(sumtime, sumobjs)



if __name__ == '__main__':
    # the place where we will find the needed source objects
    if sys.platform == 'win32':
        T_INPATH = 'd:\\__files'
    elif sys.platform == 'darwin':
        T_INPATH = '/Volumes/dev/__files'
    else:
        sys.exit('source path is undefined')

    # the paths in which we will store the objects
    T_PATHS = {}
    for i in range (0, 256):
        T_PATHS[i] = normpath('{}/p{:03}'.format(T_STARTPATH, i))

    print("--> Init <hcptarget> object")
    try:
        hcptarget = hcpsdk.target(T_NAMESPACE, T_DAAC, T_DAAC_PWD, T_PORT)
    except hcpsdk.HcpsdkError as e:
        sys.exit("Fatal: {}".format(e.errText))

    input('==> Press Enter to start the process: ')

    print("--> Init {} <connection> object(s)".format(T_THREADS))
    conns = []
    conntimes = 0.0
    outer_contime = time.time()
    for i in range(0, T_THREADS):
        try:
            conns.append(hcpsdk.connection(hcptarget, debuglevel=0))
        except Exception as e:
            sys.exit('Exception: {}'.format(str(e)))
        else:
            conntimes += conns[i].connect_time
    outer_contime = time.time() - outer_contime

    print('\tAverage inner connection time: {:,.5f}'.format(conntimes/T_THREADS))
    print('\tAverage outer connection time: {:,.5f}'.format(outer_contime))

    # load one of the files into memory
    print('--> Loading test object into memory - ', end='')
    with open(join(T_INPATH,T_OBJS[T_OBJ]), 'rb') as inHdl:
        buf = bytearray(inHdl.read())
        size = len(buf)
        print('object size = {}'.format(size))

    # Create the output paths
    outpaths = {}
    for i in range(0, T_THREADS):
        outpaths[i] = []
        for j in range(0, T_CNT_PER_THREAD):
            outpaths[i].append(join(T_STARTPATH, 't-{:03}'.format(i), '{}.{:03}'.format(T_OUTNAME, j)))

    # now write the objects...
    print('--> Now ingesting objects:')
    sumtime = 0.0
    sumobjs = 0
    outer_contime = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=T_THREADS) as executor:
        f = {executor.submit(t_write, conns[i], outpaths[i], buf): i for i in range(0,T_THREADS)}
        for future in concurrent.futures.as_completed(f):
            try:
                (stime, sobjs) = future.result()
            except Exception as exc:
                print('t-{} generated an exception: {}'.format('...', exc))
            else:
                sumtime += stime
                sumobjs += sobjs
    outer_contime = time.time() - outer_contime
    print('\t        Inner summary time:  {:,.5f} ({} objects)'.format(sumtime, sumobjs))
    print('\tAverage inner service time:  {:,.5f} ({:5,.2f} Mb/sec)'.format(sumtime / T_THREADS / sumobjs,
                                                                          (T_THREADS*sumobjs*size)/sumtime/1024/1024),
          flush=True)
    print('\tAverage outer service time:  {:,.5f} ({:5,.2f} Mb/sec)'.format(outer_contime,
                                                                          (T_THREADS*sumobjs*size)/outer_contime/1024/1024),
          flush=True)

    # now reading the objects...
    print('--> Now reading objects:')
    sumtime = 0.0
    sumobjs = 0
    outer_contime = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=T_THREADS) as executor:
        f = {executor.submit(t_read, conns[i], outpaths[i]): i for i in range(0,T_THREADS)}
        for future in concurrent.futures.as_completed(f):
            try:
                (stime, sobjs) = future.result()
            except Exception as exc:
                print('t-{} generated an exception: {}'.format('...', exc))
            else:
                sumtime += stime
                sumobjs += sobjs
    outer_contime = time.time() - outer_contime
    print('\t        Inner summary time:  {:,.5f} ({} objects)'.format(sumtime, sumobjs))
    print('\tAverage inner service time:  {:,.5f} ({:5,.2f} Mb/sec)'.format(sumtime / T_THREADS / sumobjs,
                                                                          (T_THREADS*sumobjs*size)/sumtime/1024/1024),
          flush=True)
    print('\tAverage outer service time:  {:,.5f} ({:5,.2f} Mb/sec)'.format(outer_contime,
                                                                          (T_THREADS*sumobjs*size)/outer_contime/1024/1024),
          flush=True)

    # now deleting objects...
    print('--> Now deleting objects:')
    sumtime = 0.0
    sumobjs = 0
    outer_contime = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=T_THREADS) as executor:
        f = {executor.submit(t_delete, conns[i], outpaths[i]): i for i in range(0,T_THREADS)}
        for future in concurrent.futures.as_completed(f):
            try:
                (stime, sobjs) = future.result()
            except Exception as exc:
                print('t-{} generated an exception: {}'.format('...', exc))
            else:
                sumtime += stime
                sumobjs += sobjs
    outer_contime = time.time() - outer_contime
    print('\t        Inner summary time:  {:,.5f} ({} objects)'.format(sumtime, sumobjs))
    print('\tAverage inner service time:  {:,.5f}'.format(sumtime / T_THREADS / sumobjs))
    print('\tAverage outer service time:  {:,.5f}'.format(outer_contime))


    # close the session
    for con in conns:
        con.close()
