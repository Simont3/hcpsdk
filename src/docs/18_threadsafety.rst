Thread safety
=============

These classes **are** thread-safe:

    *   :ref:`hcpsdk.Target() <hcpsdk_target>`

        Within an application, create one *Target()* object per HCP you need
        to connect to.

    *   :ref:`hcpsdk.ips.Circle() <hcpsdk_ips_circle>`

        This class is intended as an internal class for *hcpsdk.Target()*, so
        normally there is no need to instantiate it directly.

These classes **are not** thread-safe:

    *   :ref:`hcpsdk.Connection() <hcpsdk_connection>`

        A *Connection()* should be used within a single thread, only
        (or you need to provide your own locks to orchestrate usage).

    *   :ref:`hcpsdk.namespace.Info() <hcpsdk_namespace_info>`

    *   :ref:`hcpsdk.pathbuilder.PathBuilder() <hcpsdk_pathbuilder_pathbuilder>`

    *   :ref:`hcpsdk.mapi.Logs() <hcpsdk_mapi_logs>`

    *   :ref:`hcpsdk.mapi.Replication() <hcpsdk_mapi_replication>`

        These classes create their own *hcpsdk.Connection()* uppon the provided
        *hcpsdk.Target()*, each of them needs to stay within a single thread:


