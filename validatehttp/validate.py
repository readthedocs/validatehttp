'''
Load and run validation rules

This module runs the actual validation rules, by performing HTTP requests and
comparing the given responses to rulesets loaded by the rule spec.
'''

# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os.path
from collections import namedtuple

from requests import Session
from requests.exceptions import SSLError, ConnectionError

from .spec import JsonValidatorSpec, YamlValidatorSpec


class Validator(object):
    '''Create object to run validation

    :param spec: Validation spec instance
    :type spec: ValidatorSpec
    :param host: Host address to perform requests against
    :param port: Host port to perform requests against
    '''

    def __init__(self, spec, host=None, port=None):
        self.spec = spec
        self.host = host
        self.port = port

    def __repr__(self):
        return '<Validator spec={spec}>'.format(**self.__dict__)

    @classmethod
    def load(cls, spec_file, host=None, port=None):
        '''Load spec from file and return an validator instance'''
        (_, fileext) = os.path.splitext(spec_file)
        if fileext.lower() == '.json':
            spec = JsonValidatorSpec.load(spec_file)
        elif fileext.lower() == '.yaml':
            spec = YamlValidatorSpec.load(spec_file)
        else:
            raise ValueError('Unsupported file type')
        return cls(spec, host, port)

    def validate(self):
        '''Run validation using HTTP requests against validation host

        Using rules provided by spec, perform requests against validation host
        for each rule. Request response is verified to match the spec respsonse
        rule.  This will yield either a :py:cls:`ValidationPass` or
        :py:cls:`ValidationFail` response.
        '''
        session = Session()
        for rule in self.spec.get_rules():
            req = rule.get_request(self.host, self.port)
            try:
                resp = session.send(req.prepare(), allow_redirects=False)
                if rule.matches(resp):
                    yield ValidationPass(rule=rule, request=req, response=resp)
            except (ConnectionError, SSLError) as exc:
                # No response yet
                yield ValidationFail(rule=rule, request=req, response=None,
                                     error=exc)
            except ValueError as exc:
                # Response received, validation error
                yield ValidationFail(rule=rule, request=req, response=resp,
                                     error=exc)


ValidationPass = namedtuple('ValidationPass', ['rule', 'request', 'response'],
                            verbose=False)
ValidationFail = namedtuple('ValidationFail',
                            ['rule', 'request', 'response', 'error'],
                            verbose=False)
