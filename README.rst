validatehttp
============

``validatehttp`` is a command line utility used to write integration tests for
web servers using HTTP requests. Test specifications singal the HTTP request
parameters and the intended response parameters to check against. If there are
any discrepencies between the intended response and the actual resopnse, a
failure is noted.

``validatehttp`` can be used on the command line, useful for writing and
maintaining spec rulesets, or even running as a continuous integration test.

It can also be used as a Nagios plugin, for automating checks against production
servers.

Usage:
^^^^^^

validatehttp
------------

.. program:: validatehttp

.. option:: -f <file>

    Specification file to use in validation checks

.. option:: -H <host>

    Hostname to direct requests to. The default is to use the hostname from the
    request specification.

.. option:: -p <port>

    Port to direct requests to. The default is to use the implied port from the
    request specification.

.. option:: -v

    Enable verbose output

.. option:: -V

    Skip SSL verification

.. option:: -d

    Show debug output
