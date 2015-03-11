:mod:`hcpsdk` --- object access
============================================

.. automodule:: hcpsdk
   :synopsis: Framework for HCP access.

**hcpsdk** provides access to HCP through http[s]/\ :term:`reST` dialects.

Setup is easy (:ref:`see example below <hcpsdk_example>`):

    1.  Instantiate an *Authorization* object with the required credentials.

        This class will be queried by *Target* objects for authorization
        tokens.

    2.  **Optional:** create an *SSL context* if you want to have certificates
        presented by HCP validated.

    3.  Instantiate a *Target* class with HCPs *Full Qualified Domain Name*,
        the port to be used, the *Authorization* object, optionally the
        *SSL context* created in 2. and -eventually- the :term:`FQDN` of a replica HCP.

    4.  Instantiate one or more *Connection* objects.

        These objects are the workhorses of the *hcpsdk* - they are providing
        the access methods needed. You'll need to consult the respective HCP
        manuals to find out how to frame the required requests.

        *Connection* objects will open a session to HCP as soon as
        needed, but not before. After use, they keep the session open for an
        adjustable amount of time, helping to speed up things for an subsequent request.

        Don't forget to close *Connection* objects when finished with them!


Methods
^^^^^^^

.. py:method:: version()

   Return the full version of the HCPsdk (|release|).


Classes
^^^^^^^

.. autoclass:: NativeAuthorization
   :members:

.. autoclass:: DummyAuthorization
   :members:

.. autoclass:: Target
   :members:

   **Class constants:**

   .. attribute:: I_NATIVE

      HCP's http/REST dialect for access to HCPs authenticated :term:`namespaces <Namespace>`.

   .. attribute:: I_DUMMY

      HCP's http dialect for access to HCPs :term:`Default Namespace <Default Namespace>`.

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

      The :term:`FQDN` for which the Target was initialized (string).

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

.. autoexception:: HcpsdkCantConnectError

   Used to signal that a connection couldn't be established.

   .. attribute:: reason

      An error description.

.. autoexception:: HcpsdkTimeoutError

   Used to signal a Connection timeout.

   .. attribute:: reason

      An error description.

.. autoexception:: HcpsdkCertificateError

   Raised if the *SSL context* could doesn't verify a certificate
   presented by HCP.

   .. attribute:: reason

      An error description.

.. autoexception:: HcpsdkReplicaInitError

   Used to signal that the Target for a replica HCP couldn't be
   initialized (typically, this is a name resolution problem). **If
   this exception is raised, the primary Target's init failed, too.**
   You'll need to retry!

   .. attribute:: reason

      An error description.


.. _hcpsdk_example:

Example
^^^^^^^

::

    >>> import hcpsdk
    >>> hcpsdk.version()
    '0.9.0-2'
    >>> auth = hcpsdk.NativeAuthorization('n', 'n01')
    >>> t = hcpsdk.Target('n1.m.hcp1.snomis.local', auth, port=443)
    >>> c = hcpsdk.Connection(t)
    >>> c.connect_time
    '0.000000000010'
    >>>
    >>> r = c.PUT('/rest/hcpsdk/test1.txt', body='This is an example',
                  params={'index': 'true'})
    >>> c.response_status, c.response_reason
    (201, 'Created')
    >>>
    >>> r = c.HEAD('/rest/hcpsdk/test1.txt')
    >>> c.response_status, c.response_reason
    (200, 'OK')
    >>> c.getheaders()
    [('Date', 'Sat, 31 Jan 2015 20:34:53 GMT'),
     ('Server', 'HCP V7.1.0.10'),
     ('X-RequestId', '38AD86EF250DEB35'),
     ('X-HCP-ServicedBySystem', 'hcp1.snomis.local'),
     ('X-HCP-Time', '1422736493'),
     ('X-HCP-SoftwareVersion', '7.1.0.10'),
     ('ETag', '"68791e1b03badd5e4eb9287660f67745"'),
     ('Cache-Control', 'no-cache,no-store'),
     ('Pragma', 'no-cache'),
     ('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT'),
     ('Content-Type', 'text/plain'),
     ('Content-Length', '18'),
     ('X-HCP-Type', 'object'),
     ('X-HCP-Size', '18'),
     ('X-HCP-Hash', 'SHA-256 47FB563CC8F86DC37C86D08BC542968F7986ACD81C97B'
                    'F76DB7AD744407FE117'),
     ('X-HCP-VersionId', '91055133849537'),
     ('X-HCP-IngestTime', '1422736466'),
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
     ('X-HCP-ChangeTimeMilliseconds', '1422736466446.00'),
     ('X-HCP-ChangeTimeString', '2015-01-31T21:34:26+0100'),
     ('Last-Modified', 'Sat, 31 Jan 2015 20:34:26 GMT')
    ]
    >>>
    >>> r = c.GET('/rest/hcpsdk/test1.txt')
    >>> c.response_status, c.response_reason
    (200, 'OK')
    >>> c.read()
    b'This is an example'
    >>> c.service_time2
    0.0005471706390380859
    >>>
    >>> r = c.DELETE('/rest/hcpsdk/test1.txt')
    >>> c.response_status, c.response_reason
    (200, 'OK')
    >>> c.service_time2
    0.0002570152282714844
    >>>
    >>> c.close()
    >>>

