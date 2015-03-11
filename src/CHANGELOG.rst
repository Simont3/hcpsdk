Release History
===============

**0.9.2-10 2015-03-11**

*   Fixed:

    fixed an issue in *hcpsdk.Connection.request()* that led to situations
    where a failed connection wasn't recovered correctly.

**0.9.2-9 2015-03-09**

*   Fixed:

    added missing import of subpackage pathbuilder into hcpsdk.__init__.py

**0.9.2-8 2015-03-09**

*   Fixed:

    as *socket.getaddrinfo()* seems to double the resolved IP addresses under
    some circumstances, added a check to make sure we don't have duplicates
    in the result of *hcpsdk.ips.query()*

**0.9.2-7 2015-03-09**

*   Fixed:

    dependency handling, again...

**0.9.2-6 2015-03-08**

*   Fixed:

    now handling *ConnectionAbortedError* properly in hcpsdk.Connection()
    by closing and re-opening the connection on the same target IP
    address

**0.9.2-5 2015-03-07**

*   Fixed:

    __all__ in several modules, some typos in comments

**0.9.2-4 2015-03-06**

*   Fixed:

    added the missing param keyword argument to hcpsdk.Connection.PUT()

**0.9.2-3 2015-03-06**

*   Fixed:

    a missing import in hcpsdk.__init__.py that led to an unrecoverable
    error when running on Python 3.4.3

**0.9.2-1 2015-03-01**

*   Changed:

    hcpsdk.Connection.request() now logs exception information
    and stack trace if a catched exception is re-raised as an
    *hcpsdk.[..]Error*. This will get visible only if the application
    has initialized the logging subsystem.

**0.9.1-8 2015-02-27**

*   Fixed:

    Fixed line width in documentation (.rst files) to match
    limitations for pdf generation

**0.9.1-7 2015-02-27**

*   Fixed:

    pip distribution fixed to allow auto-install of dependencies
    when running 'pip install hcpsdk'

**0.9.1-6 2015-02-18**

*   Added:

    Automatic retires for hcpsdk.Connection.request() in case of a
    timeout or connection abort. A DummyAuthorization class for use
    with the Default Namespace. An appendiy on the difference when
    working with the Default Namespace
