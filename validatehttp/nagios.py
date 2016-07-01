"""Nagios interface to spec rule testing"""

# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

from pynag.Plugins import simple as Plugin  # noqa

from .validate import Validator, ValidationPass, ValidationFail


class CheckURLSpecPlugin(Plugin):

    def __init__(self, *args, **kwargs):
        self.shortname = 'checkurlspec'
        self.version = 0.1

        # Non-object based class in pynag
        Plugin.__init__(self, *args, **kwargs)

        # Add arguments
        self.add_arg('f', 'file', 'Spec file to parse')
        self.add_arg('p', 'port', 'Host HTTP port', required=False)
        self.add_arg('V', 'no-verify', 'No HTTPS verification', required=False,
                     action='store_false')
        self.must_threshold = False

    @classmethod
    def run(cls):
        """Create instance of validator for Nagios output"""
        self = cls()
        self.activate()
        spec_file = self['file']
        host = self['host']
        port = None
        if self['port'] is not None:
            port = self['port']
        verify = self['no-verify']
        if verify is None:
            verify = True

        # Build, test validator
        validator = Validator.load(spec_file, host, port, verify=verify)
        results = list(validator.validate())
        passed = [result for result in results
                  if isinstance(result, ValidationPass)]
        failures = [result for result in results
                    if isinstance(result, ValidationFail)]

        if len(list(failures)) == 0:
            self.add_message('OK', '{0}/{0} Spec tests passed'
                             .format(len(results)))
        else:
            self.add_message('CRITICAL',
                             'Passed {passed}/{count} ({failures} failures)'
                             .format(count=len(results), passed=len(passed),
                                     failures=len(failures)))
            for result in failures:
                self.add_message('CRITICAL',
                                 'spec {0} failed'
                                 .format(result.rule.uri))
        (code, message) = self.check_messages(joinstr=', ')
        self.nagios_exit(code, message)
