import sys
import hcpsdk

if __name__ == '__main__':

    #try:
    t = hcpsdk.target('n1.m.hcp73.archivas.com', 'n', 'n01',
                      replica_fqdn='n1.m.hcp72.archivas.com')
    #except hcpsdk.HcpsdkReplicaInitError as e:
    #    sys.exit(e)

    print('primary =',t.fqdn, t.addresses)
    print('replica =', t.replica.fqdn, t.replica.addresses)
