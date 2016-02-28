:mod:`hcpsdk.ips` --- name resolution
=====================================

..  automodule:: hcpsdk.ips
    :synopsis: Name resolution through :term:`DNS`

**hcpsdk.ips** provides name resolution service and IP address caching.
Used by *hcpsdk* internally; exposed here as it might be useful alone.

Functions
---------

query
^^^^^

..  autofunction:: query


Classes
-------

..  _hcpsdk_ips_circle:

Circle
^^^^^^

..  autoclass:: Circle
    :members:

    **Read-only class attributes:**

    ..  attribute:: _addresses

        List of the cached IP addresses

    **Class methods:**

Response
^^^^^^^^

..  autoclass:: Response
    :members:

    **Read-only class attributes:**

    ..  attribute:: ips

        List of resolved IP addresses (as strings)

    ..  attribute:: fqdn

        The :term:`FQDN` for which the resolve happened.

    ..  attribute:: cache

        False if the local :term:`DNS` cache has been by-passed, True if the
        system-default resolver was used.

    ..  attribute:: raised

        Empty string when no Exception were raised, otherwise the Exception's error message.


Exceptions
----------

..  autoexception:: IpsError


