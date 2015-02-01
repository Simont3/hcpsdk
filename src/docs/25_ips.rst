:mod:`hcpsdk.ips` --- name resolution
=====================================

.. automodule:: hcpsdk.ips
   :synopsis: Name resolution through DNS

**hcpsdk.ips** provides name resolution service and IP address caching.
Used by *hcpsdk* internally; exposed here as it might be useful alone.

Classes
^^^^^^^

.. autoclass:: Circle
   :members:

   **Read-only class attributes:**

       .. attribute:: _addresses

          List of the cached IP addresses

   **Class methods:**

.. autoclass:: Response
   :members:

   **Read-only class attributes:**

       .. attribute:: ips

          List of resolved IP addresses (as strings)

       .. attribute:: fqdn

          The FQDN for which the resolve happened.

       .. attribute:: cache

          False if the local DNS cache has been by-passed, True if the system-default
          resolver was used.

       .. attribute:: raised

          Empty string when no Exception were raised, otherwise the Exception's error message.


Functions
^^^^^^^^^

.. autofunction:: query


Exceptions
^^^^^^^^^^

.. autoexception:: IpsError

   .. attribute:: reason

      An error description.


