SSL certificate verification
======================================

.. Warning::

    **hcpsdk** doesn't verify SSL certificates presented by HCP,
    per default.

For the case that SSL certificate verification is desired, **hcpsdk**
allows to do so without excessive effort:

    *   Make sure the SSL certificate presented by HCP contains the IP
        addresses (!) of all HCP nodes as *Subject Alternative Names*.

    *   Create an *SSL context* and assign it to the **Target**
        object during creation. Each **Connection** created using that
        **Target** will automatically inherit the *SSL context*.

Here are some hints:

    *   This example creates an *SSL context* with the recommended security
        settings for client sockets, including automatic certificate
        verification against the system's trusted CA store:

        .. code-block:: python
           :emphasize-lines: 1

            >>> context = ssl.create_default_context()
            >>> auth = hcpsdk.NativeAuthorization('n', 'n01')
            >>> t = hcpsdk.Target('n1.m.hcp1.snomis.local', auth,
                                 port=443, sslcontext=context)

    *   Alternatively, you can create an *SSL context* that verifies
        certificates against a local CA file:

        .. code-block:: python
           :emphasize-lines: 1

            >>> context = ssl.create_default_context(cafile='myCA.pem')
            >>> auth = hcpsdk.NativeAuthorization('n', 'n01')
            >>> t = hcpsdk.Target('n1.m.hcp1.snomis.local', auth,
                                  port=443, sslcontext=context)

If you want to have more control about the protocol and/or the cipher
suites in use, follow the `Python documentation about SSL context creation
<https://docs.python.org/3/library/ssl.html?highlight=ssl.sslcontext#ssl.SSLContext>`_\ .
