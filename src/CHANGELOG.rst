0.9.2-1 2015-03-01
------------------
Changed:    hcpsdk.Connection.request() now logs exception information
            and stack trace if a catch'd exception is re-raised as an
            hcpsdk.*Error. This will get visible only if the application
            has initialized the logging subsystem.
Added:      -
Fixed:      -

0.9.1-8 2015-02-27
------------------
Changed:    -
Added:      -
Fixed:      Fixed line width in documeantion (.rst files) to match
limitations for pdf generation

0.9.1-7 2015-02-27
------------------
Changed:    -
Added:      -
Fixed:      pip distribution fixed to allow auto-install of dependencies
            when running 'pip install hcpsdk'

0.9.1-6 2015-02-18
------------------
Changed:    -
Added:      Automatic retires for hcpsdk.Connection.request() in case of a
            timeout or connection abort.
            A DummyAuthorization class for use with the Default Namespace
            An appendiy on the difference when working with the Default
            Namespace
Fixed:      -

Version Date
------------------
Changed:    -
Added:      -
Fixed:      -