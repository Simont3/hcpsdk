HCPsdk
======

HCPsdk provides a simple SDK to access an Hitachi Content Platform (HCP)
from Python3. It handles name resolution, multiple sessions spread across all
available HCP nodes, persistent connections and recovery from failing
connections.

It's that easy:

::

    >>> import hcpsdk

    >>> # initialize an *Authorization* object
    >>> auth = hcpsdk.NativeAuthorization('user', 'password')

    >>> # initialize a *Target* object
    >>> t = hcpsdk.Target("namespace.tenant.hcp.your.domain",
                          auth, port=443)

    >>> # initialize a Connection to the `Target``
    >>> c = hcpsdk.Connection(t)

    >>> # do something with the connection...
    >>> r = c.GET('/rest/your_file.txt')
    >>> c.response_status, c.response_reason
    (200, 'OK')
    >>> r.read()
    b'some data...'
    >>>
    >>> c.close()


Features
--------

- Handles HCP as a target object
- Connection objects, while tied to a target object, allow
  access to HCP through HCPs native http/REST dialect
- Higher level modules provide easy access to namespace
  statistics and some MAPI functionality, along with
  the ability to create unique object names / paths

Dependencies
------------

**hcpsdk** depends on `dnspython <http://www.dnspython.org>`_, which is used
for non-cached name resolution when bypassing the system's resolver.


Documentation
-------------

To be found at `readthedocs.org <http://hcpsdk.readthedocs.org>`_

Installation
------------

Install hcpsdk by running:

    ``pip install hcpsdk``

    -or-

    * get the source from `GitHub <https://github.com/simont3/hcpsdk/archive/master.zip>`_
    * unzip the archive
    * run ``python setup.py install``

    -or-

    * Fork at `Github <https://github.com/simont3/hcpsdk>`_

Contribute
----------

- Issue Tracker: `<https://github.com/simont3/hcpsdk/issues>`_
- Source Code: `<https://github.com/simont3/hcpsdk>`_

Support
-------

If you find any bugs, please let me know via the Issue Tracker;
if you have comments or suggestions, send an email to `<sw@snomis.de>`_

License
-------

The MIT License (MIT)

Copyright (c) 2014-2015 Thorsten Simons (sw@snomis.de)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
