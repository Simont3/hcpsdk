:mod:`hcpsdk.mapi` --- MAPI access
==================================

.. automodule:: hcpsdk.mapi
   :synopsis: Access to selected Management API (MAPI) functionality.

**hcpsdk.mapi** provides access to selected MAPI functions.


Classes
^^^^^^^

.. autoclass:: replication

   **Class constants:**

   Link types:

       .. attribute:: R_ACTIVE_ACTIVE

          Active/Active link

       .. attribute:: R_OUTBOUND

          Outbound link (active/passive)

       .. attribute:: R_INBOUND

          Inbound link (active/passive)

   Link activities:

       .. attribute:: R_SUSPEND

          Suspend a link (all link types)

       .. attribute:: R_RESUME

          Resume a suspended link (all link types)

       .. attribute:: R_RESTORE

          Restore a link (all link types)

       .. attribute:: R_FAILOVER

          Initiate a failover (all link types)

       .. autoattribute:: R_FAILBACK

          Initiate a failback (ACTIVE/ACTIVE links only)

       .. autoattribute:: R_BEGINRECOVERY

          Begin recovery (INBOUND links only)

       .. autoattribute:: R_COMPLETERECOVERY

          Complete recovery (INBOUND links only)

   **Class methodes:**

   .. automethod:: getReplicationSettings

      .. attribute:: returned dictionary (example):

         ::

            {'allowTenantsToMonitorNamespaces': 'true',
             'enableDNSFailover': 'true',
             'enableDomainAndCertificateSynchronization': 'true',
             'network': '[hcp_system]'}

   .. automethod:: getLinkList

      .. attribute:: returned list (example):

         ::

            ['hcp1-a-a-hcp2']

   .. automethod:: getLinkDetails

      .. attribute:: the returned dictionary (example):

         ::

            {'compression': 'false',
             'connection': {'localHost': '192.168.0.52, 192.168.0.53, 192.168.0.54, '
                                         '192.168.0.55',
                            'localPort': '5748',
                            'remoteHost': '192.168.0.56, 192.168.0.57, 192.168.0.58, '
                                          '192.168.0.59',
                            'remotePort': '5748'},
             'description': 'active/active link between HCP1 and HCP2',
             'encryption': 'false',
             'failoverSettings': {'local': {'autoFailover': 'false',
                                            'autoFailoverMinutes': '120'},
                                  'remote': {'autoFailover': 'false',
                                             'autoFailoverMinutes': '120'}},
             'id': 'b9c488db-f641-486e-a8b4-56810faf23cd',
             'name': 'hcp1-a-a-hcp2',
             'priority': 'OLDEST_FIRST',
             'statistics': {'bytesPending': '0',
                            'bytesPendingRemote': '0',
                            'bytesPerSecond': '0.0',
                            'bytesReplicated': '0',
                            'errors': '0',
                            'errorsPerSecond': '0.0',
                            'objectsPending': '0',
                            'objectsPendingRemote': '0',
                            'objectsReplicated': '0',
                            'operationsPerSecond': '0.0',
                            'upToDateAsOfMillis': '1419975449113',
                            'upToDateAsOfString': '2014-12-30T22:37:29+0100'},
             'status': 'GOOD',
             'statusMessage': 'Synchronizing data',
             'suspended': 'false',
             'type': 'ACTIVE_ACTIVE'}


   .. automethod:: setReplicationLinkState


Exceptions
^^^^^^^^^^

.. autoexception:: ReplicationSettingsError

   .. attribute:: reason

      An error description.


Example
^^^^^^^

::

    >>> import hcpsdk.mapi
    >>> from pprint import pprint
    >>>
    >>> t = hcpsdk.target('admin.hcp1.snomis.local', 'service', 'service01', port=9090)
    >>> r = hcpsdk.mapi.replication(t)
    >>> l = r.getLinkList()
    >>> l
    ['hcp1-a-a-hcp2']
    >>>
    >>> d = r.getLinkDetails(l[0])
    >>> pprint(d)
    {'compression': 'false',
     'connection': {'localHost': '192.168.0.52, 192.168.0.53, 192.168.0.54, '
                                 '192.168.0.55',
                    'localPort': '5748',
                    'remoteHost': '192.168.0.56, 192.168.0.57, 192.168.0.58, '
                                  '192.168.0.59',
                    'remotePort': '5748'},
     'description': 'active/active link between HCP1 and HCP2',
     'encryption': 'false',
     'failoverSettings': {'local': {'autoFailover': 'false',
                                    'autoFailoverMinutes': '120'},
                          'remote': {'autoFailover': 'false',
                                     'autoFailoverMinutes': '120'}},
     'id': 'b9c488db-f641-486e-a8b4-56810faf23cd',
     'name': 'hcp1-a-a-hcp2',
     'priority': 'OLDEST_FIRST',
     'statistics': {'bytesPending': '0',
                    'bytesPendingRemote': '0',
                    'bytesPerSecond': '0.0',
                    'bytesReplicated': '0',
                    'errors': '0',
                    'errorsPerSecond': '0.0',
                    'objectsPending': '0',
                    'objectsPendingRemote': '0',
                    'objectsReplicated': '0',
                    'operationsPerSecond': '0.0',
                    'upToDateAsOfMillis': '1420122209230',
                    'upToDateAsOfString': '2015-01-01T15:23:29+0100'},
     'status': 'GOOD',
     'statusMessage': 'Synchronizing data',
     'suspended': 'false',
     'type': 'ACTIVE_ACTIVE'}
    >>>

