MAPI - Replication management
=============================

.. automodule:: hcpsdk.mapi
   :synopsis: Access to selected Management API (:term:`MAPI`) functionality.

This class allows to query HCP for replication links, their settings and
state. It also allows to trigger a replication link failover anf failback.

.. Note::

  To be able to use this class, HCP needs to run at least
  **version 7.0**.


Classes
^^^^^^^

.. _hcpsdk_mapi_replication:

.. autoclass:: Replication

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

       .. attribute:: R_FAILBACK

          Initiate a failback (ACTIVE/ACTIVE links only)

       .. attribute:: R_BEGINRECOVERY

          Begin recovery (INBOUND links only)

       .. attribute:: R_COMPLETERECOVERY

          Complete recovery (INBOUND links only)

   **Class methodes:**

   .. automethod:: getreplicationsettings

      .. attribute:: returned dictionary (example):

         ::

            {'allowTenantsToMonitorNamespaces': 'true',
             'enableDNSFailover': 'true',
             'enableDomainAndCertificateSynchronization': 'true',
             'network': '[hcp_system]'}

   .. automethod:: getlinklist

      .. attribute:: returned list (example):

         ::

            ['hcp1-a-a-hcp2']

   .. automethod:: getlinkdetails

      .. attribute:: the returned dictionary (example):

         ::

            {'compression': 'false',
             'Connection': {'localHost': '192.168.0.52, 192.168.0.53, 192.168.0.54, '
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


   .. automethod:: setreplicationlinkstate


Exceptions
^^^^^^^^^^

.. autoexception:: ReplicationSettingsError


Example
^^^^^^^

::

    >>> import hcpsdk.mapi
    >>> from pprint import pprint
    >>>
    >>> auth = hcpsdk.NativeAuthorization('service', 'service01')
    >>> t = hcpsdk.Target('admin.hcp1.snomis.local', auth, port=9090)
    >>> r = hcpsdk.mapi.Replication(t)
    >>> l = r.getlinklist()
    >>> l
    ['hcp1--<-->--hcp2']
    >>> d = r.getlinkdetails(l[0])
    >>> pprint(d)
    {'compression': 'false',
     'connection': {'localHost': '192.168.0.52, 192.168.0.53, '
                                 '192.168.0.54, 192.168.0.55',
                    'localPort': '5748',
                    'remoteHost': '192.168.0.56, 192.168.0.57, '
                                  '192.168.0.58, 192.168.0.59',
                    'remotePort': '5748'},
     'description': 'active/active replication between HCP1 and HCP2',
     'encryption': 'false',
     'failoverSettings': {'local': {'autoFailover': 'false',
                                    'autoFailoverMinutes': '120'},
                          'remote': {'autoFailover': 'false',
                                     'autoFailoverMinutes': '120'}},
     'id': '81b6df01-2bda-4094-aed8-0c47e68bd820',
     'name': 'hcp1--<-->--hcp2',
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
                    'upToDateAsOfMillis': '1422701963994',
                    'upToDateAsOfString': '2015-01-31T11:59:23+0100'},
     'status': 'GOOD',
     'statusMessage': 'Synchronizing data',
     'suspended': 'false',
     'type': 'ACTIVE_ACTIVE'}
    >>>
