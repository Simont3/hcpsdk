Working with replicated HCP systems
===================================

HCP features replication of ingested objects to one or more other HCP
systems:

*   Up to version 6, HCP supported active/passive replication, where the
    primary HCP (to be specific, the Tenants/Namespaces configured for
    replication) are in read/write mode, where the replication target HCP is
    in read-only mode.

*   HCP version 7 added support for active/active replication.
    In this mode, the Tenants/Namespaces participating in a replicaton link
    are in read-write mode on both HCP systems.

A replication links is always configured to connect two HCP systems.
As active/passive replication alway requires one system to be in read-only
mode, write access to the other system is possible if the replication link
is in failed-over state, only.

Active/active replication, on the other hand, allows write access to
both HCP systems in a link.

:ref:`hcpsdk.Target() <hcpsdk_target>` can be configured to make use of the
replication system automatically. It does this by creating a background
*hapsdk.Target()* pointing to the replication target HCP. Various modes of
operation are provided and can be activated when the *hcpsdk.Target()*
object is instanciated:

*   RS_READ_ALLOWED

    Allow to read from replica (always)

*   RS_WRITE_ALLOWED

    Allow write to replica (always, A/A links only)

*   RS_READ_ON_FAILOVER

    Automatically read from replica when the primary isn't available

*   RS_WRITE_ON_FAILOVER

    Allow write to replica when failed over



