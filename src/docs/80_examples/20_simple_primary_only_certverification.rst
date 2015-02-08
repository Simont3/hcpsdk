Simple object I/O without replica, with SSL certificate verification
====================================================================

Code sample
-----------

This code sample is exactly the same as the one shown as
:doc:`10_simple_primary_only`, except that we verify the SSL certificate
presented by HCP against a CA certificate chain we have locally on file.
So, described here are only the differences to the first code sample.

We need to import **ssl.create_default_context** and define a file that
holds our CA certificate chain:

    .. literalinclude:: code/simple_primary_only_certverify.py
       :language: python
       :start-after: # start sample block 10
       :end-before:  # end sample block 10
       :emphasize-lines: 3,15-16

Now, we create an *SSL context* and use it when instantiating
our **Target** object:

    .. literalinclude:: code/simple_primary_only_certverify.py
       :language: python
       :start-after: # start sample block 17
       :end-before:  # end sample block 20
       :emphasize-lines: 7,11


Sample code output
------------------

.. rubric:: Certificate verification success, with debug messages

.. literalinclude:: output/debug_simple_primary_only_certverify.txt
   :emphasize-lines: 12

.. rubric:: Certificate verification failed, with debug messages

(**P_CAFILE** has been changed to a file holding a non-matching CA chain)

.. literalinclude:: output/debug_simple_primary_only_certverify_fail.txt
   :emphasize-lines: 12,20,23
