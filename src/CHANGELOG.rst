Release History
===============

**0.9.4-8 2017-07-14**

*   Fixed a bug where URLs containing '+' also have to be url-encoded

**0.9.4-7 2017-07-07**

*   Fixed a bug where already url-encoded URLs were url-encoded, again

**0.9.4-6 2017-03-31**

*   Fixed a bug in NativeADAuthorization that caused 403 errors
    (thanks to Kevin L)

**0.9.4-5 2016-12-19**

*   Fixed a bug in setup.py that caused dnspython3 still be called in

**0.9.4-4 2016-12-06**

*   Changed the pre-requisite from dnspython3 to dnspython >= 1.15.0.
    (dnspython 1.15.0 supports Python 2 and 3)

**0.9.4-3 2016-02-28**

*   Added the posibility to enable TCP keep-alive for *hcpsdk.Connection*\ s
*   Documentation slightly reformatted

**0.9.4-2 2016-02-04**

*   Re-worked the representation of *Target()'s* and *Connection()'s*
    (mainly) read-only attributes; fixed documentation source accordingly
*   Renamed attribute *Response* to *response* in *hcpsdk.Connection()*\.
    *Response* is deprecated, but will stay available for backward
    compatibility

**0.9.4-1 2015-12-18**

*   Fixed doctring of *hcpsdk.mapi.replication.setreplicationlinkstate()*

**0.9.4-0 2015-12-17**

*   Added *hcpsdk.mapi.chargeback*
*   Added *hcpsdk.mapi.tenant* (with limited functionality)
*   Added support for Active Directory users
    (*hcpsdk.NativeADAuthorization()*)
*   Added trademarks to documentation

**0.9.3.11 2015-12-06**

*   Fixed a bug that lead *Connection.service_time2* to be too low

**0.9.3.10 2015-12-01**

*   Added support for local Swift Authorization (w/o Keystone and
*   an article about the proper use of URLs

**0.9.3-9 2015-11-08**

*   Documentation fixes

**0.9.3-7 2015-11-08**

*   Fixed return value of *mapi.log.download()*
*   Made output of *mapilogshell.py* more precise

**0.9.3-6 2015-10-20**
**0.9.3-5 2015-10-20**

*   Removed alabaster from the list of dependencies for source installs

**0.9.3-4 2015-10-12**
**0.9.3-3 2015-10-12**

*   Fixed a bug in setup.py to enable pip install on Windows

**0.9.3-2 2015-10-12**

*   Changed README.md and setup.py to adopt to Gitlab and readthedocs
    requirements

**0.9.3-1 2015-10-11**

*   Documentation fixes

**0.9.3-0 2015-10-10**

*   Added access to the *logs* endpoint invented with HCP 7.2
    (*hcpsdk.mapi.Logs()*)
*   Provide an example script, based on cmd.cmd() to manually explore the
    log download MAPI. See documentation.
*   Splitted *hcpsdk.mapi* classes into separate packages (*logs* and
    *replication*, yet), while maintaining accessibility through
    *hcpsdk.mapi.Logs* and *hcpsdk.mapi.Replication*, respectively.
*   Corrected the documentation buildout for Exceptions
*   Fixed a bug that prevented internal connections to be closed when
    idletimer fired
*   Fixed the logger initialization per class throughout the entire
    code base
*   Added exception handling for *ConnectionRefusedError*

**0.9.2-38 2015-08-31**

*   Added documentation about thread-safety.

**0.9.2-37 2015-08-18**

*   Handle OSError by retry-ing the call in
    *hcpsdk.Connection.request()*
*   *Connection.close()* now clears the underlying socket
    reference
*   *Connection.close()* no more generates debug message if the
    connection wasn't open.
*   repr(*hcpsdk.Target*) and repr(*hcpsdk.Connection*) now returns
    the memory address of the respecive object for debug purposes.

**0.9.2-36 2015-07-15**

*   Disabled character '+' as save when urlencoding parameters in
    *hcpsdk.Connection.request()*

**0.9.2-35 2015-06-23**

*   Removed some of the annoying debug messages stating idleTimer
    stopped/started

**0.9.2-34 2015-06-23**

*   Now showing the number of bytes read in debug output in
    *hcpsdk.Connection.read()*

**0.9.2-32 2015-06-02**

*   Now catching BrokenPipeError during *hcpsdk.Connection.request()*,
    leading to as many retries as requested for the connection.

**0.9.2-31 2015-05-26**

*   Fixed pip installer pre-requisites

**0.9.2-30 2015-05-24**

*   Fixed pip installer pre-requisites
*   Documentation for *hcpsdk.namespace*: added hint about HCP version
    availability.

**0.9.2-29 2015-05-20**

*   Fixed proper handling of http.client.CannotSendRequest in
    *Connection.request()*

**0.9.2-28 2015-05-20**

*   If a socket.timeout is raised in *hcpsdk.Connection.read()*, re-raise
    it as *hcpsdk.HcpsdkTimeoutError*.

**0.9.2-27 2015-05-19**

*   *hcpsdk.Connection.request()* is now aware of ResponseNotReady being
    raised during *http.client.HTTPConnection.getresponse()* and retries
    appropriately.

**0.9.2-26 2015-05-19**

*   Corrected the behaviour of the 'all' parameter in
    hcpsdk.namespace.listaccessiblens()

**0.9.2-25 2015-05-13**

*   One more debug message right after getResponse()

**0.9.2-24 2015-05-13**

*   Added output of service_time2 to debug messages

**0.9.2-23 2015-05-13**

*   Output of service times in debug messages set to 17 digits

**0.9.2-22 2015-05-13**

*   Output of service times in debug messages are more precise, now

**0.9.2-21 2015-03-28**

*   Tuned the exception handling in *hcpsdk.request()*
*   Fixed/added testcases

**0.9.2-20 2015-03-26**

*   Fixed/added testcases

**0.9.2-19 2015-03-26**

*   *hcpsdk.Connection.request()*: changed behavior for the cases where we
    receive one of ConnectionAbortedError, http.client.ResponseNotReady,
    TimeoutError and socket.timeout. We now refresh the cached IP
    addresses and setup a new connection.

**0.9.2-18 2015-03-25**

*   *hcpsdk.Connection.request()* accidentally quoted blanks in an URL as '+',
    which is not valid for HCP. Replaced *urllib.parse.quote_plus()* by
    *urllib.parse.quote()*.

**0.9.2-17 2015-03-24**

*   *hcpsdk.Connection.request()* is now aware of timeouts that occur
    during *http.client.HTTPConnection.getresponse()* and retries
    appropriately.

**0.9.2-16 2015-03-22**

*   *hcpsdk.Connection.close()* now checks if the underlying connection
    is really open before trying to close it.

**0.9.2-15 2015-03-22**

*   *hcpsdk.Connection.request()* excluded '+' from being urlencoded in
    params.

**0.9.2-14 2015-03-20**

*   *hcpsdk.Connection.POST()* now allows to add a body to the request.

**0.9.2-13 2015-03-16**

*   Changed some unnecessary logging.error calls to logging.debug

**0.9.2-12 2015-03-16**

*   Now raising HcpsdkReplicaInitError id a *hcpsdk.Target* is initialized with
    a replica HCP (not yet implemented).
*   Improved error handling in *hcpsdk.Connection.request()*.
*   *hcpsdk.Target()* will now raise *ips.IpsError* if DNS name resolution
    fails.

**0.9.2-11 2015-03-12**

*   Fixed an issue in *hcpsdk.Connection.__str__()* where a false attribute
    was referenced.

**0.9.2-10 2015-03-11**

*   Fixed an issue in *hcpsdk.Connection.request()* that led to situations
    where a failed connection wasn't recovered correctly.

**0.9.2-9 2015-03-09**

*   Added missing import of subpackage pathbuilder into hcpsdk.__init__.py

**0.9.2-8 2015-03-09**

*   Fixed:

    as *socket.getaddrinfo()* seems to double the resolved IP addresses under
    some circumstances, added a check to make sure we don't have duplicates
    in the result of *hcpsdk.ips.query()*

**0.9.2-7 2015-03-09**

*   Fixed dependency handling, again...

**0.9.2-6 2015-03-08**

*   Now handling *ConnectionAbortedError* properly in hcpsdk.Connection()
    by closing and re-opening the connection on the same target IP
    address

**0.9.2-5 2015-03-07**

*   Fixed __all__ in several modules, some typos in comments

**0.9.2-4 2015-03-06**

*   Added the missing param keyword argument to hcpsdk.Connection.PUT()

**0.9.2-3 2015-03-06**

*   Fixed a missing import in hcpsdk.__init__.py that led to an unrecoverable
    error when running on Python 3.4.3

**0.9.2-1 2015-03-01**

*   hcpsdk.Connection.request() now logs exception information
    and stack trace if a catched exception is re-raised as an
    *hcpsdk.[..]Error*. This will get visible only if the application
    has initialized the logging subsystem.

**0.9.1-8 2015-02-27**

*   Fixed line width in documentation (.rst files) to match
    limitations for pdf generation

**0.9.1-7 2015-02-27**

*   Fixed pip distribution fixed to allow auto-install of dependencies
    when running 'pip install hcpsdk'

**0.9.1-6 2015-02-18**

*   Added automatic retires for hcpsdk.Connection.request() in case of a
    timeout or connection abort,
*   A DummyAuthorization class for use with the Default Namespace,
*   An appendiy on the difference when working with the Default Namespace.
