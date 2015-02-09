Glossary
========

.. glossary::
    :sorted:

    reST
        *representational State Transfer*

        An architectural approach for client/server communication for
        performance, scalability, simplicity, reliability and more.
        See `the Wikipedia entry <http://en.wikipedia.org/wiki/Representational_state_transfer>`_
        for more details.

    Tenant
        A Tenant within HCP is an administrative entity that allows to configure and
        manage a set of :term:`namespaces <Namespace>` within a configurable storage quota, along with the
        user account required to access data.

    Namespace
        A Namespace is a addressable data store, separated from other namespaces, having
        an individual filesystem-like structure, several access protocols along with a
        set of other configurables.

    Data Access Account
        A local user within a :term:`Tenant`

    HS3
        Amazon S3 compatible interface

    HSwift
        OpenStack Swift compatible interface

    MAPI
        Management API - a :term:`reSTful <reST>` interface to manage HCP

    DNS
        Domain Name System - used to translate a :term:`FQDN` to IP addresses

    FQDN
        Full Qualified Domain Name (*namespace.tenant.hcp.domain.com*)