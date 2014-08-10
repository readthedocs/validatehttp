# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

from pynag.Plugins import simple as Plugin

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
        self.must_threshold = False

    @classmethod
    def run(cls):
        self = cls()
        self.activate()
        spec_file = self['file']
        host = self['host']
        port = None
        if self['port'] is not None:
            port = self['port']

        # Build, test validator
        validator = Validator.load(spec_file, host, port)
        results = list(validator.validate())
        failures = [result for result in results
                    if isinstance(result, ValidationFail)]
        if len(failures) > 0:
            print(failures)
