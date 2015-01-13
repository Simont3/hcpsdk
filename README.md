HCPsdk
======

HCPsdk provides a simple SDK to access an Hitachi Content Platform (HCP)
from Python3. It handles nameresolution, multiple sessions spread across all
available HCP nodes, persistent connections and recovery from failing
connections.

Usage:
------

::

    import hcpsdk

    # initialize a ``target`` object
    hcptarget = hcpsdk.target("n1.m.hcp2.snomis.local",
                              "n", "n01", port=443,
                              header_mode=hcpsdk.target.HEADER_6UP)

    cons = []
    for i in range(0,4):
        # initialize a connection to the `target``
        cons.append(hcpsdk.connection(hcptarget))

    # do something with the connections...


License
=======

The MIT License (MIT)

Copyright (c) 2014 Thorsten Simons (sw@snomis.de)

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
