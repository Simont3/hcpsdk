Appendix 1 - Default Namespace
==============================

**hcpsdk** is primarily targeting the :term:`authenticated Namespaces <Namespace>`
invented with HCP version 3.

Nevertheless, it is possible to use **hcpsdk** with the legacy :term:`Default Namespace`
by taking notice of a few differences:

*   As there is no user authentication with the Default Namespace, use the
    *hcpsdk.DummyAuthorization* class as the *authorization* argument when
    instantiating an *hcpsdk.Target*

*   Different from authenticated Namespaces, the root folder for requests is
    ``/fcfs_data`` (instead of ``/rest``)

*   An *HEAD* request for an object stored in the Default Namespace will yield very
    limited object metadata, only. If you need more, you need to request the
    metadata by a *GET* from ``/fcfs_metadata/your/path/to/object/core-metadata.xml``

*   The Default Namespace can have a single annotation (custom metadata), only.
    You need to request it by a *GET* from ``/fcfs_metadata/your/path/to/object/custom-metadata.xml``

*   Several actions you can trigger by a *POST* request to an authenticated Namespace need
    to be executed by a *PUT* to one of the files in ``/fcfs_metadata/your/path/to/object/``.


..  Note::

    Consult the manual **Using the Default Namespace** available from the HCP
    System and Tenant Management Consoles for details about working with the
    Default Namespace.


Example
^^^^^^^

::

    >>> import hcpsdk
    >>>
    >>> auth = hcpsdk.DummyAuthorization()
    >>> t = hcpsdk.Target('default.default.hcp1.snomis.local', auth, port=443)
    >>> c = hcpsdk.Connection(t)
    >>> c.connect_time
    '0.000000000010'
    >>>
    >>> r = c.PUT('/fcfs_data/hcpsdk/test1.txt', body='This is an example', params={'index': 'true'})
    >>> c.response_status, c.response_reason
    (201, 'Created')
    >>>
    >>> r = c.HEAD('/fcfs_data/hcpsdk/test1.txt')
    >>> c.response_status, c.response_reason
    (200, 'OK')
    >>> c.getheaders()
    [('Date', 'Wed, 18 Feb 2015 16:48:49 GMT'),
     ('Server', 'HCP V7.1.0.10'),
     ('X-ArcServicedBySystem', 'hcp1.snomis.local'),
     ('X-ArcClusterTime', '1424278129'),
     ('X-RequestId', '6BB17FCE72FECA84'),
     ('X-HCP-ServicedBySystem', 'hcp1.snomis.local'),
     ('X-HCP-Time', '1424278129'),
     ('X-HCP-SoftwareVersion', '7.1.0.10'),
     ('ETag', '"68791e1b03badd5e4eb9287660f67745"'),
     ('Cache-Control', 'no-cache,no-store'),
     ('Pragma', 'no-cache'),
     ('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT'),
     ('Content-Type', 'text/plain'),
     ('Content-Length', '18'),
     ('X-ArcPermissionsUidGid', 'mode=0100400; uid=0; gid=0'),
     ('X-ArcTimes', 'ctime=1424278066; mtime=1424278066; atime=1424278065'),
     ('X-ArcSize', '18')]
    >>>
    >>> r = c.GET('/fcfs_data/hcpsdk/test1.txt')
    >>> c.response_status, c.response_reason
    (200, 'OK')
    >>> c.read()
    b'This is an example'
    >>> c.service_time2
    0.00039696693420410156
    >>>
    >>> r = c.DELETE('/fcfs_data/hcpsdk/test1.txt')
    >>> c.response_status, c.response_reason
    (200, 'OK')
    >>> c.service_time2
    0.0001819133758544922
    >>>
    >>> c.close()
