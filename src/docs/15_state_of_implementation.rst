State of implementation
=======================

*  Handle HCP as a **target** object, responsible for IP address resolution
   (by-passing the local DNS cache, per default) and assigning IP addresses
   out of a cached pool to **connection** objects.
   As of today, it handles the native http/REST interface, only. Support for
   HS3 and HSwift are planned.

*  Provide **connection** objects related to **target** objects, responsible
   for traffic handling, service time measurement as well as handling of errors
   and timeouts. Connections are persistent for a configurable idle time, and
   are automatically re-connected on next use, if they timed out on idle.

*  Easy access to Namespace information and statistics.

*  The **pathbuilder** subpackage builds a path/name combination to be used to
   store an object into HCP, keeping the number of needed folders low.

*  Provide access to to the Management API (MAPI). This is very restricted today,
   but will be extended on the authors personal needs. Available today:

   *  Replication link information, link failover/failback.
