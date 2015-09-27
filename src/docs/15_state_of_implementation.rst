State of Implementation
=======================

**Release** |release|

*   Handle HCP as a *Target* object, responsible for IP address resolution
    (by-passing the local :term:`DNS` cache, per default) and assigning IP addresses
    out of an internally cached pool to *Connection* objects.
    As of today, it handles the native http/:term:`reST` interface. Support for
    :term:`HS3` and :term:`HSwift` is planned.

    Support for automated usage of a replicated HCP will be implemented soon,
    with various usage strategies available.

*   Supports verification of SSL certificates presented by HCP when using https
    against a private CA chain file or the system's trusted CA store. Default
    is not to verify certificates.

*   Provide *Connection* objects related to *Target* objects, responsible
    for traffic handling, service time measurement as well as handling of errors
    and timeouts. Connections are persistent for a configurable idle time, and
    are automatically re-connected on next use, if they timed out on idle.

*   Easy access to :term:`namespace <Namespace>` information and statistics.

*   The :doc:`pathbuilder <35_pathbuilder>` subpackage builds a path/name
    combination to be used to store an object into HCP, keeping the number of
    needed folders low.

*   Provide convenience methods for the :term:`Management API (MAPI) <MAPI>`. This
    is a bit limited today, but will be extended primarily on the authors needs.
    Available today:

    *   Log file download (requires at least HCP 7.2)

        ..  versionadded:: 0.9.3

    *   Replication link information, link failover/failback (requires at leat HCP 7.0)
