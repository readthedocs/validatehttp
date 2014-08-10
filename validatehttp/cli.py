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
        stats = {'pass': 0, 'fail': 0, 'count': 0}
        for result in self.validator.validate():
            stats['count'] += 1
            if isinstance(result, ValidationPass):
                stats['pass'] += 1
                if self.verbose:
                    print('Pass: spec {0}'.format(result.rule.uri))
            elif isinstance(result, ValidationFail):
                stats['fail'] += 1
                print('Fail: spec {0} failed: {1}'
                      .format(result.rule.uri, result.error))
        print('Passed {pass}/{count} ({fail} failures)'.format(**stats))

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
