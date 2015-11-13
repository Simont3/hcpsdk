MAPI - Chargeback Resources
===========================

.. versionadded:: 0.9.4

.. automodule:: hcpsdk.mapi
   :synopsis: Access to selected Management API (:term:`MAPI`) functionality.

This class allows to request chargback reports from HCP.


Classes
^^^^^^^

.. _hcpsdk_mapi_chargeback:

.. autoclass:: Chargeback

   **Class constants:**

  Collection periods:

     .. attribute:: CBG_DAY
     .. attribute:: CBG_HOUR
     .. attribute:: CBG_TOTAL

  Output formats:

     .. attribute:: CBM_CSV
     .. attribute:: CBM_JSON
     .. attribute:: CBM_XML


   **Class attributes**


   **Class methodes:**

   .. automethod:: request

   .. automethod:: close


Exceptions
^^^^^^^^^^

.. autoexception:: ChargebackError

Sample Code
^^^^^^^^^^^

None, yet.

Sample Output
^^^^^^^^^^^^^

None, yet.
