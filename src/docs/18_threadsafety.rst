Thread safety
=============

**hcpsdk** is partially thread-safe:

*   :ref:`hcpsdk.Target() <hcpsdk_target>` **is** thread-safe.

    Within an application, create one *Target()* object per HCP you need
    to connect to.

*   :ref:`hcpsdk.Connection() <hcpsdk_connection>` **is not**
    thread-safe.

    A *Connection()* should be used within a single thread, only
    (or you need to provide your own locks to orchestrate usage).

*   :ref:`hcpsdk.ips.Circle() <hcpsdk_ips_circle>` **is** thread-safe.

    This class is intended as an internal class for *hcpsdk.Target()*, so
    normally there is no need to instantiate it directly.

*   :ref:`hcpsdk.namespace.Info() <hcpsdk_namespace_info>` **is not**
    thread-safe.

    This class creates its own *hcpsdk.Connection()* uppon the provided
    *hcpsdk.Target()*, it needs to stay within a single thread.

*   :ref:`hcpsdk.pathbuilder.PathBuilder() <hcpsdk_pathbuilder_pathbuilder>`
    **is not** thread-safe.

*   :ref:`hcpsdk.mapi.Replication() <hcpsdk_mapi_replication>` **is not**
    thread-safe.

    This class creates its own *hcpsdk.Connection()* uppon the provided
    *hcpsdk.Target()*, it needs to stay within a single thread.

