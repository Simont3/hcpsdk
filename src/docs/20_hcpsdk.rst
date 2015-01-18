:mod:`hcpsdk` --- object access
============================================

.. automodule:: hcpsdk
   :synopsis: Framework for HCP access.

**hcpsdk** provides functionality for access to HCP, where *Target()*  acts
as a central object per HCP Target (and its replica, eventually) and
*Connection()* provides methods for REST access.

Methods
^^^^^^^

.. py:method:: version()

   Returns the full version of the HCPsdk (|release|).

Classes
^^^^^^^

.. autoclass:: Target
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

      The FQDN for which the Target was initialized (string).

   .. attribute:: port

      The port used by the Target (int).

   .. attribute:: ssl

      Target initialized for SSL (bool).

   .. attribute:: addresses

      The IP addresses used by this Target (list).

   .. attribute:: headers

      The http headers prepared for this Target (dictionary).

   .. attribute:: replica

      The replica Target, if available (an *hcpsdk.Target* object or None).

   **Class methods:**

.. autoclass:: Connection
   :members:

   **Read-only class attributes:**

   .. attribute:: address

      The IP address used for this Connection.

   .. attribute:: Response

      Exposition of the http.client.Response object for the last Request.

   .. attribute:: response_status

      The HTTP status code of the last Request.

   .. attribute:: response_reason

      The corresponding HTTP status message.

   .. attribute:: connect_time

      The time the last connect took.

   .. attribute:: service_time1

      The time the last action on a Request took. This can be the initial part
      of PUT/GET/etc. or a single (possibly incomplete) read from
      a Response.

   .. attribute:: service_time2

      Duration of the complete Request up to now. Sum of all ``service_time1``
      during handling a Request.

   **Class methods:**


Exceptions
^^^^^^^^^^

.. autoexception:: HcpsdkError

   Used to signal a generic error in **hcpsdk**.

   .. attribute:: reason

      An error description.

.. autoexception:: HcpsdkTimeoutError

   Used to signal a Connection timeout.

   .. attribute:: reason

      An error description.

.. autoexception:: HcpsdkReplicaInitError

   Used to signal that the Target for a replica HCP couldn't be
   initialized (typically, this is a name resolution problem). **If
   this exception is raised, the primary Target's init failed, too.**
   You'll need to retry!

   .. attribute:: reason

      An error description.


Example
^^^^^^^

::

    >>> import hcpsdk
    >>> hcpsdk.version()
    '0.9.0-1'
    >>> t = hcpsdk.Target('n1.m.hcp1.snomis.local', 'n', 'n01')
    >>> c = hcpsdk.Connection(t)
    >>> c.connect_time
    0.000000000010
    >>>
    >>> r = c.PUT('/rest/hcpsdk/test1.txt', body='This is an example', params={'index': 'true'})
    >>> c.response_status, c.response_reason
    (201, 'Created')
    >>>
    >>> r = c.HEAD('/rest/hcpsdk/test1.txt')
    >>> c.response_status, c.response_reason
    (200, 'OK')
    >>> c.getheaders()
    [('Date', 'Sun, 18 Jan 2015 14:22:23 GMT'),
     ('Server', 'HCP V7.0.1.17'),
     ('X-RequestId', 'AA6FF1E05A49375'),
     ('X-HCP-ServicedBySystem', 'hcp1.snomis.local'),
     ('X-HCP-Time', '1421590943'),
     ('X-HCP-SoftwareVersion', '7.0.1.17'),
     ('ETag', '"68791e1b03badd5e4eb9287660f67745"'),
     ('Cache-Control', 'no-cache,no-store'),
     ('Pragma', 'no-cache'),
     ('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT'),
     ('Content-Type', 'text/plain'),
     ('Content-Length', '18'),
     ('X-HCP-Type', 'object'),
     ('X-HCP-Size', '18'),
     ('X-HCP-Hash', 'SHA-256 47FB563CC8F86DC37C86D08BC542968F7986ACD81C97BF76DB7AD744407FE117'),
     ('X-HCP-VersionId', '90981819023489'),
     ('X-HCP-IngestTime', '1421590922'),
     ('X-HCP-RetentionClass', ''),
     ('X-HCP-RetentionString', 'Deletion Allowed'),
     ('X-HCP-Retention', '0'),
     ('X-HCP-IngestProtocol', 'HTTP'),
     ('X-HCP-RetentionHold', 'false'),
     ('X-HCP-Shred', 'false'),
     ('X-HCP-DPL', '2'),
     ('X-HCP-Index', 'true'),
     ('X-HCP-Custom-Metadata', 'false'),
     ('X-HCP-ACL', 'false'),
     ('X-HCP-Owner', 'n'),
     ('X-HCP-Domain', ''),
     ('X-HCP-UID', ''),
     ('X-HCP-GID', ''),
     ('X-HCP-CustomMetadataAnnotations', ''),
     ('X-HCP-Replicated', 'false'),
     ('X-HCP-ReplicationCollision', 'false'),
     ('X-HCP-ChangeTimeMilliseconds', '1421590922263.00'),
     ('X-HCP-ChangeTimeString', '2015-01-18T15:22:02+0100'),
     ('Last-Modified', 'Sun, 18 Jan 2015 14:22:02 GMT')]
    >>>
    >>> r = c.GET('/rest/hcpsdk/test1.txt')
    >>> c.response_status, c.response_reason
    (200, 'OK')
    >>> c.read()
    b'This is an example'
    >>> c.service_time2
    0.0004937648773193359
    >>>
    >>> r = c.DELETE('/rest/hcpsdk/test1.txt')
    >>> c.response_status, c.response_reason
    (200, 'OK')
    >>> c.service_time2
    0.00019121170043945312
    >>>
    >>> c.close()
    >>>

