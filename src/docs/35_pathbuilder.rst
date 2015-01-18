:mod:`hcpsdk.pathbuilder` --- unique object names
=================================================

Due to its internals, bulk ingest activity into HCP delivers best
possible performance if multiple parallel writes are directed to
different folders take place.

This subpackage offers functionality to create
an unique object name along with a pseudo-random path to a
folder to store the object in.

The object name generated is an UUID version 1, as defined in
`RFC 4122 <http://tools.ietf.org/pdf/rfc4122.pdf>`_\ . The algorithm uses (one of)
the servers MAC addresses, along with the system time to create
the UUID.


Classes
^^^^^^^

.. automodule:: hcpsdk.pathbuilder
   :synopsis: Create an unique object name path
   :members:


Exceptions
^^^^^^^^^^

.. autoexception:: PathBuilderError

    Used to signal an error during unique object name generation or object
    name to path mapping.

   .. attribute:: reason

      An error description.

