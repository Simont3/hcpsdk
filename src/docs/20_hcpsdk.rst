:mod:`hcpsdk` --- object access
============================================

.. automodule:: hcpsdk
   :synopsis: Framework for HCP access.

**hcpsdk** provides functionality for access to HCP, where *target()*  acts
as a central object per HCP target (and its replica, eventually) and
*connection()* provides methods for REST access.

Classes
^^^^^^^

.. autoclass:: target
   :members:

   **Class constants:**

   .. attribute:: I_NATIVE

      HCP's http/REST dialect for access to HCPs authenticated namespaces.

   .. attribute:: I_HS3

      The Amazon S3 compatible HS3 REST dialect.
      *-not yet implemented-*

   .. attribute:: I_HSWIFT

      The OpnStack Swift compatible HSWIFT dialect.
      *-not yet implemented-*

   .. attribute:: RS_READ_ALLOWED

      Allow to read from replica (always)

   .. attribute:: RS_READ_ON_FAILOVER

      Automatically read from replica when failed over

   .. attribute:: RS_WRITE_ALLOWED

      Allow write to replica (always, **A/A links only**)

   .. attribute:: RS_WRITE_ON_FAILOVER

      Allow write to replica when failed over

   **Read-only class attributes:**

   .. attribute:: fqdn

      The FQDN for which the target was initialized (string).

   .. attribute:: port

      The port used by the target (int).

   .. attribute:: ssl

      Target initialized for SSL (bool).

   .. attribute:: addresses

      The IP addresses used by this target (list).

   .. attribute:: headers

      The http headers prepared for this target (dictionary).

   .. attribute:: replica

      The replica target, if available (an *hcpsdk.target* object or None).

   **Class methods:**

.. autoclass:: connection
   :members:

   **Read-only class attributes:**

   .. attribute:: address

      The IP address used for this connection.

   .. attribute:: response

      Exposition of the http.client.response object for the last request.

   .. attribute:: response_status

      The HTTP status code of the last request.

   .. attribute:: response_reason

      The corresponding HTTP status message.

   .. attribute:: connect_time

      The time the last connect took.

   .. attribute:: service_time1

      The time the last action on a request took. This can be the initial part
      of PUT/GET/etc. or a single (possibly incomplete) read from
      a response.

   .. attribute:: service_time2

      Duration of the complete request up to now. Sum of all ``service_time1``
      during handling a request.

   **Class methods:**


Exceptions
^^^^^^^^^^

.. autoexception:: HcpsdkError

   Used to signal a generic error in **hcpsdk**.

   .. attribute:: reason

      An error description.

.. autoexception:: HcpsdkTimeoutError

   Used to signal a connection timeout.

   .. attribute:: reason

      An error description.

.. autoexception:: HcpsdkReplicaInitError

   Used to signal that the target for a replica HCP couldn't be
   initialized (typically, this is a name resolution problem). **If
   this exception is raised, the primary target's init failed, too.**
   You'll need to retry!

   .. attribute:: reason

      An error description.


Example
^^^^^^^

::

   >>> import hcpsdk
   >>> t = hcpsdk.target('n1.m.hcp1.snomis.local', 'n', 'n01')
   >>> c = hcpsdk.connection(t)
   >>> '{:0.12f}'.format(c.connect_time)
   '0.000000000010'
   >>>
   >>> r = c.PUT('/rest/hcpsdk/test1.txt', body='This is an example')
   >>> c.response_status, c.response_reason
   (201, 'Created')
   >>> c.getheaders()
   [('Date', 'Wed, 07 Jan 2015 12:55:43 GMT'),
    ('Server', 'HCP V7.0.1.17'),
    ('X-HCP-ServicedBySystem', 'hcp1.snomis.local'),
    ('Location', '/rest/hcpsdk/test1.txt'),
    ('X-HCP-VersionId', '90920662012865'),
    ('X-HCP-Hash',
     'SHA-256 47FB563CC8F86DC37C86D08BC542968F7986ACD81C97BF76DB7AD744407FE117'),
     ('ETag', '"68791e1b03badd5e4eb9287660f67745"'),
     ('X-RequestId', 'BA44338AD9E4EB48'),
     ('X-HCP-Time', '1420635343'),
     ('Content-Length', '0')
   ]
   >>>
   >>> r = c.GET('/rest/hcpsdk/test1.txt')
   >>> c.response_status, c.response_reason
   (200, 'OK')
   >>> c.read()
   b'This is an example'
   >>> '{:0.12f}'.format(c.service_time2)
   '0.015625000000'
   >>>
   >>> c.close()
   >>>