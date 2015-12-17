MAPI - Chargeback Resources
===========================

..  versionadded:: 0.9.4

..  automodule:: hcpsdk.mapi
    :synopsis: Access to selected Management API (:term:`MAPI`) functionality.

This class allows to request chargback reports from HCP.

| HCP needs to have MAPI enabled for the system itself as well as for every
  *Tenant* to collect from.
| A system-level user can collect summed-up reports from all *Tenants* that
  have MAPI enabled; he can collect *Namespace*-level reports from all
  *Tenants* that have granted system-level admin access.
| A *Tenant*-level admin can collect reports for *Namespaces* as well as
  a summed-up report for the *Tenant* itself.


Classes
^^^^^^^

..  _hcpsdk_mapi_chargeback:

..  autoclass:: Chargeback

    **Class constants:**

        Collection periods:

            .. attribute:: CBG_DAY
            .. attribute:: CBG_HOUR
            .. attribute:: CBG_TOTAL

        Output formats:

            .. attribute:: CBM_CSV
            .. attribute:: CBM_JSON
            .. attribute:: CBM_XML


    **Class methodes**

        .. automethod:: request

        .. automethod:: close


Exceptions
^^^^^^^^^^

.. autoexception:: ChargebackError

Sample Code
^^^^^^^^^^^

Note that the last record in this example shows the *Tenants* overall values,
while the the record before shows statistics for a single *Namespace*.

::

    >>> import hcpsdk
    >>> auth = hcpsdk.NativeAuthorization('service', 'service01')
    >>> tgt = hcpsdk.Target('admin.hcp73.archivas.com', auth,
                            port=hcpsdk.P_MAPI)
    >>> cb = hcpsdk.mapi.Chargeback(tgt)
    >>> result = cb.request(tenant='m',
                            granularity=hcpsdk.mapi.Chargeback.CBG_TOTAL,
                            fmt=hcpsdk.mapi.Chargeback.CBM_JSON)
    >>> print(result.read())
    {
      "chargebackData" : [ {
        "systemName" : "hcp73.archivas.com",
        "tenantName" : "m",
        "namespaceName" : "n1",
        "startTime" : "2015-11-04T15:27:29+0100",
        "endTime" : "2015-12-17T20:35:33+0100",
        "valid" : false,
        "deleted" : "false",
        "bytesOut" : 0,
        "reads" : 0,
        "writes" : 0,
        "deletes" : 0,
        "tieredObjects" : 0,
        "tieredBytes" : 0,
        "metadataOnlyObjects" : 0,
        "metadataOnlyBytes" : 0,
        "bytesIn" : 0,
        "storageCapacityUsed" : 25306468352,
        "ingestedVolume" : 25303387299,
        "objectCount" : 7219
      }, {
        "systemName" : "hcp73.archivas.com",
        "tenantName" : "m",
        "startTime" : "2015-11-04T15:27:29+0100",
        "endTime" : "2015-12-17T20:35:33+0100",
        "valid" : false,
        "deleted" : "false",
        "bytesOut" : 2156,
        "reads" : 2,
        "writes" : 1,
        "deletes" : 1,
        "tieredObjects" : 0,
        "tieredBytes" : 0,
        "metadataOnlyObjects" : 0,
        "metadataOnlyBytes" : 0,
        "bytesIn" : 5944,
        "storageCapacityUsed" : 25607081984,
        "ingestedVolume" : 25427708304,
        "objectCount" : 65607
      } ]
    }
    >>> cb.close()

