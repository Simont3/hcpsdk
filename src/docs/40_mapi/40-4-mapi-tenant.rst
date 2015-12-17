MAPI - Tenant Resources
=======================

..  versionadded:: 0.9.4

..  automodule:: hcpsdk.mapi
    :synopsis: Access to selected Management API (:term:`MAPI`) functionality.

This class allows to work with the *Tenant* resources in HCP.

| HCP needs to have MAPI enabled at the system-level.


Methods
^^^^^^^
..  autofunction:: listtenants



Classes
^^^^^^^

..  _hcpsdk_mapi_tenant:

..  autoclass:: Tenant

    **Class attributes**

    ..  attribute:: name

        The name of the Tenant represented by this object.

    **Class methods**

    ..  automethod:: info

    ..  automethod:: close

Exceptions
^^^^^^^^^^

.. autoexception:: TenantError

Sample Code
^^^^^^^^^^^



..  code-block:: text
    :emphasize-lines: 13-19

    >>> from pprint import pprint
    >>> import hcpsdk
    >>> auth = hcpsdk.NativeAuthorization('service', 'service01')
    >>> tgt = hcpsdk.Target('admin.hcp73.archivas.com', auth, port=hcpsdk.P_MAPI)
    >>> tenants = hcpsdk.mapi.listtenants(tgt)
    >>> pprint(tenants)
    [<hcpsdk.mapi.tenant.Tenant object at 0x1032ce6a0>,
     <hcpsdk.mapi.tenant.Tenant object at 0x1032ce748>,
     <hcpsdk.mapi.tenant.Tenant object at 0x1032ce7b8>,
     <hcpsdk.mapi.tenant.Tenant object at 0x1032ce828>,
     <hcpsdk.mapi.tenant.Tenant object at 0x1032ce898>,
     <hcpsdk.mapi.tenant.Tenant object at 0x1032ce908>]
    >>> tenants[0].name
    'Default'
    >>> pprint(tenants[0].info())
    {'snmpLoggingEnabled': False,
     'syslogLoggingEnabled': False,
     'systemVisibleDescription': '',
     'tenantVisibleDescription': ''}

..  Warning::

    | The :term:`Default Tenant` has far less properties compared to the
      :term:`usual Tenants <Tenant>` HCP provides.
    | See :doc:`Appendix 1 <../A0_appendixes/A1_apdx1_defns>`.

..  code-block:: text
    :emphasize-lines: 1-22

    >>> tenants[1].name
    'm'
    >>> pprint(tenants[1].info())
    {'administrationAllowed': True,
     'authenticationTypes': {'authenticationType': ['LOCAL', 'EXTERNAL']},
     'complianceConfigurationEnabled': True,
     'dataNetwork': '[hcp_system]',
     'hardQuota': '200.00 GB',
     'managementNetwork': '[hcp_system]',
     'maxNamespacesPerUser': 100,
     'name': 'm',
     'namespaceQuota': 'None',
     'replicationConfigurationEnabled': True,
     'searchConfigurationEnabled': True,
     'servicePlanSelectionEnabled': True,
     'snmpLoggingEnabled': False,
     'softQuota': 85,
     'syslogLoggingEnabled': False,
     'systemVisibleDescription': 'Der üblicherweise als erstes erzeugte Tenant...',
     'tags': {'tag': []},
     'tenantVisibleDescription': '',
     'versioningConfigurationEnabled': True}
    >>> for t in tenants:
    ...     t.close()
    ...
    >>>
