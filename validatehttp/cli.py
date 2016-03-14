# -*- coding: utf-8 -*-

"""Command line interface for testing"""

from __future__ import print_function, unicode_literals

import argparse
from collections import Counter

from termcolor import cprint

from .validate import Validator, ValidationPass, ValidationFail


class ValidatorCLI(object):
    """validatehttp - HTTP response validator"""

    def __init__(self, validator, verbose=False, debug=False):
        self.validator = validator
        self.verbose = verbose
        self.debug = debug

    def run(self):
        """Run validator with CLI output"""
        count = Counter(results=0, passes=0, failures=0)

        for result in self.validator.validate():
            count['results'] += 1
            if isinstance(result, ValidationPass):
                count['passes'] += 1
                header = '✓ Pass: {0}'.format(result.rule.uri)
                cprint(header, 'green', attrs=['bold'])
            elif isinstance(result, ValidationFail):
                count['failures'] += 1
                header = '✗ Fail: {0}'.format(result.rule.uri)
                cprint(header, 'red', attrs=['bold'])

                if self.verbose:
                    extra = (' ' * 4) + str(result.error)
                    try:
                        (expected, received) = result.mismatch()
                        extra += '\n'.join([
                            '',
                            (' ' * 8) + 'Expected: {0}'.format(expected),
                            (' ' * 8) + 'Received: {0}'.format(received),
                        ])
                    except (AttributeError, TypeError):
                        pass

                    if extra:
                        cprint(extra, 'red', attrs=['bold'])

        msg = '{passes}/{results} passed ({failures} failures)'.format(**count)
        if count['passes'] == count['results']:
            msg = ' '.join(['Passed!', msg])
            cprint('\n'.join(['-' * len(msg), msg]), 'green')
        else:
            msg = ' '.join(['Failed!', msg])
            cprint('\n'.join(['-' * len(msg), msg]), 'red')

    @classmethod
    def cli(cls):
        """Set up command line interface, process arguments"""
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
        parser.add_argument('-V', '--no-verify', dest='verify',
                            action='store_false',
                            help="Don't verify SSL connections")
        parser.add_argument('-d', '--debug', dest='debug',
                            action='store_true', help='Debug output')
        args = parser.parse_args()

        # Create validator interface from specfile, run the cli process and
        # fancy output
        validator = Validator.load(args.specfile, host=args.host,
                                   port=args.port, verify=args.verify,
                                   debug=args.debug)
        self = cls(validator, verbose=args.verbose, debug=args.debug)
        return self.run()
