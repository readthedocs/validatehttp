# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import argparse

from .validate import Validator, ValidationPass, ValidationFail


class ValidatorCLI(object):
    '''validatehttp - HTTP response validator'''

    def __init__(self, validator, verbose=False):
        self.validator = validator
        self.verbose = verbose

    def run(self):
        results = list(self.validator.validate())
        passed = [result for result in results
                  if isinstance(result, ValidationPass)]
        failures = [result for result in results
                    if isinstance(result, ValidationFail)]
        output_list = failures
        if self.verbose:
            output_list = results

        for result in output_list:
            if isinstance(result, ValidationPass):
                print('Pass: spec {0}'.format(result.rule.uri))
            elif isinstance(result, ValidationFail):
                print('Fail: spec {0} failed: {1}'
                      .format(result.rule.uri, result.error))
        print('Passed {passed}/{count} ({failures} failures)'
              .format(count=len(results), passed=len(passed),
                      failures=len(failures)))

    @classmethod
    def cli(cls):
        # Build up command interface
        parser = argparse.ArgumentParser(description=cls.__doc__)
        parser.add_argument('-H', '--host', dest='host', action='store',
                            help='Host address to test against')
        parser.add_argument('-p', '--port', dest='port', action='store',
                            help='Host port to test against')
        parser.add_argument('-f', '--file', dest='specfile', action='store',
                            help='HTTP spec file to parse', required=True)
        parser.add_argument('-v', '--verbose', dest='verbose',
                            action='store_true', help='Verbose output')
        args = parser.parse_args()

        # Create validator interface from specfile, run the cli process and
        # fancy output
        validator = Validator.load(args.specfile, host=args.host, port=args.port)
        self = cls(validator, verbose=args.verbose)
        return self.run()
