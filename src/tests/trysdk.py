import sys
import time
import pprint
import hcpsdk

print("--> Init <hcptarget> object")
try:
    hcptarget = hcpsdk.target("n1.m.hcp73.archivas.com",
                              "n", "n01", port=443)
    print("   URL:", hcptarget.fqdn)
    print("  PORT:", hcptarget.port)
    print("   IPs:", hcptarget.addresses)
    print("HEADER:", hcptarget.headers)
    print(type(hcptarget))

    docs = ['/rest/test/0072.256kbfile',
            '/rest/test/sqlite-src-3070400.zip',
            '/rest/test/Python-3.2.3.tar',
            '/rest/test/ubuntu-12.04.2-server-amd64.iso',]

    for i in [0]:
        print("<-> "*20)
        print('GET.ing {}'.format(docs[i]))

        try:
            con = hcpsdk.connection(hcptarget, debuglevel=0)
        except Exception as e:
            print('Exception: {}'.format(str(e)))
        else:
            print('\tIP = {}'.format(con.address))
            print('\tConnection time:', con.connect_time)

        time.sleep(0.1)

        try:
            r = con.request('GET', docs[i])
        except Exception as e:
            print('Exception: {}'.format(str(e)))
        else:
            print('\t', con.response_status, con.response_reason)
            size = int(con.getheader('x-hcp-size',0))
            while con.read():
                pass
            print('\tService time: {} ({:5,.2f}Mb/sec)'.format(con.service_time2, size/con.service_time2/1024/1024))



except hcpsdk.HcpsdkError as e:
    sys.exit("Fatal: " + e.errText)



