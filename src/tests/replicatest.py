import sys
import hcpsdk

if __name__ == '__main__':

    #try:
    t = hcpsdk.target('n1.m.hcp1.snomis.local', 'n', 'n01', replica_fqdn='n1.m.hcp9.snomis.local')
    #except hcpsdk.HcpsdkReplicaInitError as e:
    #    sys.exit(e)

    print('primary =',t.fqdn, t.addresses)
    print('replica =', t.replica.fqdn, t.replica.addresses)
