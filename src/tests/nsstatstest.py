import sys
import pprint
import hcpsdk

print("--> Init <hcptarget> object")
try:
    hcptarget = hcpsdk.target("n1.m.hcp73.archivas.com",
                              "n", "n01", port=443)

    try:
        nso = hcpsdk.namespace.info(hcptarget)
    except hcpsdk.HcpsdkError as e:
        sys.exit(str(e))
    else:
        print("--> actual namespace statistics:")
        r = nso.NSstatistics()
        pprint.pprint(r, width= 80)
        print(' ~> con/service time: {} / {} sec.'.format(nso.connect_time,
                                                          nso.service_time))
        print()

        print("--> list all accessible namespace's settings")
        r = nso.listAccessibleNS()
        pprint.pprint(r, width= 80)
        print(' ~> con/service time: {} / {} sec.'.format(nso.connect_time,
                                                          nso.service_time))
        print()

        print("--> list the actual namespace's settings")
        r = nso.listAccessibleNS(all=True)
        pprint.pprint(r, width= 80)
        print(' ~> con/service time: {} / {} sec.'.format(nso.connect_time,
                                                          nso.service_time))
        print()

        print("--> list the available Retention Classes")
        r = nso.listRetentionClasses()
        pprint.pprint(r, width=80)
        print(' ~> con/service time: {} / {} sec.'.format(nso.connect_time,
                                                          nso.service_time))
        print()

        print("--> list namespace and user permissions")
        r = nso.listPermissions()
        pprint.pprint(r, width=80)
        print(' ~> con/service time: {} / {} sec.'.format(nso.connect_time,
                                                          nso.service_time))
        print()


except hcpsdk.HcpsdkError as e:
    sys.exit("Fatal: " + e.errText)



