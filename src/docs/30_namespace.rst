:mod:`hcpsdk.namespace` --- namespace information
=================================================

.. automodule:: hcpsdk.namespace
   :synopsis: Namespace information

**hcpsdk.namespace** provides access to the actual Namespace's parameters and
statistics. The **hcpsdk.Target** object must have been instantiated with a
**Namespace FQDN**.

Classes
^^^^^^^

.. autoclass:: Info

   .. automethod:: nsstatistics

      .. attribute:: returned dictionary (example):

         ::

            {'customMetadataObjectBytes': 13542405,
             'customMetadataObjectCount': 380107,
             'namespaceName': 'n1',
             'objectCount': 402403,
             'shredObjectBytes': 0,
             'shredObjectCount': 0,
             'softQuotaPercent': 85,
             'totalCapacityBytes': 53687091200,
             'usedCapacityBytes': 13792362496}

   .. automethod:: listaccessiblens

      .. attribute:: returned dictionary (example):

         ::

            {'n2': {'defaultIndexValue': True,
                    'defaultRetentionValue': 0,
                    'defaultShredValue': False,
                    'description': ['replicated', 'search', 'versioning'],
                    'dpl': 2,
                    'hashScheme': 'SHA-256',
                    'name': 'n2',
                    'nameIDNA': 'n2',
                    'retentionMode': 'enterprise',
                    'searchEnabled': True,
                    'versioningEnabled': True},
             'n1': {'defaultIndexValue': True,
                    'defaultRetentionValue': 0,
                    'defaultShredValue': False,
                    'description': ['replicated', 'search', 'no versioning'],
                    'dpl': 2,
                    'hashScheme': 'SHA-256',
                    'name': 'n1',
                    'nameIDNA': 'n1',
                    'retentionMode': 'enterprise',
                    'searchEnabled': True,
                    'versioningEnabled': False}}


   .. automethod:: listretentionclasses

      .. attribute:: returned dictionary (example):

         ::

            {'initial_unspecified': {'autoDelete': False,
                                     'description': 'Retention Class with an initial '
                                                    'unspecified value.',
                                     'name': 'initial_unspecified',
                                     'value': -2},
             'deletion_prohibited': {'autoDelete': False,
                                     'description': 'Class which prohibits deletion.',
                                     'name': 'deletion_prohibited',
                                     'value': -1},
             'TAX_DATA': {'autoDelete': True,
                          'description': 'Class for tax data - actually 10 years.',
                          'name': 'TAX_DATA',
                          'value': 'A+10y'}}



   .. automethod:: listpermissions

      .. attribute:: returned dictionary (example):

         ::

            {'namespacePermissions': {'browse': True,
                                      'changeOwner': True,
                                      'delete': True,
                                      'privileged': True,
                                      'purge': True,
                                      'read': True,
                                      'readAcl': True,
                                      'search': True,
                                      'write': True,
                                      'writeAcl': True},
             'namespaceEffectivePermissions': {'browse': True,
                                               'changeOwner': True,
                                               'delete': True,
                                               'privileged': True,
                                               'purge': True,
                                               'read': True,
                                               'readAcl': True,
                                               'search': True,
                                               'write': True,
                                               'writeAcl': True},
             'userPermissions': {'browse': True,
                                 'changeOwner': True,
                                 'delete': True,
                                 'privileged': True,
                                 'purge': True,
                                 'read': True,
                                 'readAcl': True,
                                 'search': True,
                                 'write': True,
                                 'writeAcl': True},
             'userEffectivePermissions': {'browse': True,
                                          'changeOwner': True,
                                          'delete': True,
                                          'privileged': True,
                                          'purge': True,
                                          'read': True,
                                          'readAcl': True,
                                          'search': True,
                                          'write': True,
                                          'writeAcl': True}}


Example
^^^^^^^
::

    >>> import hcpsdk.namespace
    >>> from pprint import pprint
    >>> auth = hcpsdk.NativeAuthorization('n', 'n01')
    >>> t = hcpsdk.Target('n1.m.hcp1.snomis.local', auth, port=443)
    >>> n = hcpsdk.namespace.Info(t)
    >>> pprint(n.nsstatistics())
    {'customMetadataObjectBytes': 0,
     'customMetadataObjectCount': 0,
     'namespaceName': 'n1',
     'objectCount': 0,
     'shredObjectBytes': 0,
     'shredObjectCount': 0,
     'softQuotaPercent': 85,
     'totalCapacityBytes': 53687091200,
     'usedCapacityBytes': 0}
    >>>


