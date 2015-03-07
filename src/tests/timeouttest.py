import os
import time
import hcpsdk

if __name__ == '__main__':

    a = hcpsdk.NativeAuthorization('n', 'n01')
    t = hcpsdk.Target('n1.m.hcp1.snomis.local', a, port=443)
    c = hcpsdk.Connection(t)

    r = c.GET('/rest/hcpsdk/testfile2.mp4')
    print(c.response_status, c.response_reason)

    print('len(c.read(1024)) = {}'.format(len(c.read(1024))))

    for i in range(10):
        print('.', end='', flush=True)
        time.sleep(1)
    print()

    try:
        print('len(c.read()) = {}'.format(len(c.read())))
    except Exception as e:
        print(str(e))
        raise e
    finally:
        c.close()

