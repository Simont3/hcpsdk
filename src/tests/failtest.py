import sys
from os.path import join, normpath
import time
import pprint
import http.client
import hcpsdk

T_NAMESPACE = 'n1.m.hcp73.archivas.com'
T_DAAC      = 'n'
T_DAAC_PWD  = 'n01'
T_PORT      = 443
T_DEBUG     = True

T_OBJ            = 128            # the object we will use in a run (from objs)
T_NAME = '/rest/hcpsdk/failtest'  # path to write to

T_OBJ = '256kbfile'  # the source object


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
    T_OBJPATH = join(T_INPATH, T_OBJ)

    print("--> Init <hcptarget> object")
    try:
        auth = hcpsdk.NativeAuthorization(T_DAAC, T_DAAC_PWD)
        hcptarget = hcpsdk.Target(T_NAMESPACE, auth, T_PORT)
    except hcpsdk.HcpsdkError as e:
        sys.exit("Fatal: {}".format(e.errText))

    print("--> Init <connection> object")
    conntimes = 0.0
    outer_contime = time.time()
    try:
        con = hcpsdk.Connection(hcptarget, debuglevel=0, idletime=600, retries=2)
    except Exception as e:
        sys.exit('Exception: {}'.format(str(e)))

    print('--> PUT object {}'.format(T_OBJPATH))
    with open(join(T_INPATH,T_OBJ), 'rb') as inHdl:
        r = con.PUT(T_NAME, inHdl)
    print('PUT result: {}'.format(con.response_status))


    print('--> GET object {}'.format(T_OBJPATH))
    try:
        r = con.HEAD(T_NAME)
    except Exception as e:
        print(str(e))

    print('--> sleep 10 seconds')
    time.sleep(10)
    print('-' * 70)

    print('--> GET object again {}'.format(T_OBJPATH))
    try:
        r = con.GET(T_NAME)
    except Exception as e:
        print('Exception: {}'.format(str(e)))
    else:
        print('--> read')
        x = con.read()
        print('--> read {} bytes'.format(len(x)))

    print('--> Close <connection>')
    con.close()