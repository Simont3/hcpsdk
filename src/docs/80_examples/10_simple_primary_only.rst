Simple object I/O without replica
=================================

Code sample
-----------

This :download:`code sample <code/simple_primary_only.py>` shows basic usage of the SDK - ingest an object, retrieve
its metadata, read and delete it. It also shows how to retrieve request timers
and how to enable debug logging.

First, we import the needed packages and setup a few constants with the
parameters needed to access HCP. We also make sure that this program only
runs if called as such:

    .. include:: code/simple_primary_only.py
       :literal:
       :start-after: # start sample block 10
       :end-before:  # end sample block 10

We need to create an authorization object, which converts the user credentials
into the authorization token needed for HCP access.

    .. include:: code/simple_primary_only.py
       :literal:
       :start-after: # start sample block 17
       :end-before:  # end sample block 17

Now, we initialize a **Target** object with the parameters and the
authorization object created in the steps before.
Notice that we do this within a try/except clause, as we need to be able
to react on errors that might happen during initialization.

    .. include:: code/simple_primary_only.py
       :literal:
       :start-after: # start sample block 20
       :end-before:  # end sample block 20

At next, we initialize a **Connection** object, using the **Target**
created before. Notice that there is no IP address assigned to the
Connection at this time! This is because a connection will acquire an
IP address not earlier than needed.

    .. include:: code/simple_primary_only.py
       :literal:
       :start-after: # start sample block 30
       :end-before:  # end sample block 30

Now that we have a **Connection** and its corresponding **Target**, let's
write an object (the 128kb file); we'll also set some policies for it,
using the *params* argument. Again, notice the exception
handling! Now, we have an IP address assigned. If all's well, print the
hash value HCP calculated for our object:

    .. include:: code/simple_primary_only.py
       :literal:
       :start-after: # start sample block 40
       :end-before:  # end sample block 40

OK, as all was well so far, let's see if our object is really there -
we'll do an *HEAD* Request and if successful, print the returned
headers, as they contain the objects metadata:

    .. include:: code/simple_primary_only.py
       :literal:
       :start-after: # start sample block 50
       :end-before:  # end sample block 50

We'll read the object back and print the first few bytes of its
content:

    .. include:: code/simple_primary_only.py
       :literal:
       :start-after: # start sample block 60
       :end-before:  # end sample block 60

Clean up by deleting the object again:

    .. include:: code/simple_primary_only.py
       :literal:
       :start-after: # start sample block 65
       :end-before:  # end sample block 65

And finally, don't forget to close the **Connection**!
This will cleanly cancel the timer thread that keeps an idle
connection open (persistent). Not doing so will lead to the
program not finishing until the timer expires!

    .. include:: code/simple_primary_only.py
       :literal:
       :start-after: # start sample block 70
       :end-before:  # end sample block 70

As the SDK is pre-configured for DEBUG logging using Pythons native
logging facility, you simply enable it by activating a logger, set
to level DEBUG. In this example, we simply set P_DEBUG to True, which
will enable the logging facility:

    .. include:: code/simple_primary_only.py
       :literal:
       :start-after: # start sample block 15
       :end-before:  # end sample block 15


Sample code output
------------------

.. rubric:: Without debug messages

.. include:: output/print_simple_primary_only.txt
   :literal:

.. rubric:: With debug messages

.. include:: output/debug_simple_primary_only.txt
   :literal:
