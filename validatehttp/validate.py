# -*- coding: utf-8 -*-

"""
Load and run validation rules

This module runs the actual validation rules, by performing HTTP requests and
comparing the given responses to rulesets loaded by the rule spec.
"""

from __future__ import print_function, unicode_literals

import os.path
import pprint

from requests import Session
from requests.exceptions import SSLError, ConnectionError
from requests.packages import urllib3

from .spec import JsonValidatorSpec, YamlValidatorSpec, ValidationError


class Validator(object):
    """Create object to run validation

    :param spec: Validation spec instance
    :type spec: ValidatorSpec
    :param host: Host address to perform requests against
    :param port: Host port to perform requests against
    """

    def __init__(self, spec, host=None, port=None, verify=True, debug=False):
        self.spec = spec
        self.host = host
        self.port = port
        self.verify = verify
        self.debug = debug

    def __repr__(self):
        """String representation of validator instance"""
        return '<Validator spec={spec}>'.format(**self.__dict__)

    @classmethod
    def load(cls, spec_file, *args, **kwargs):
        """Load spec from file and return an validator instance"""
        (_, fileext) = os.path.splitext(spec_file)
        spec_class = None
        if fileext.lower() == '.json':
            spec_class = JsonValidatorSpec
        elif fileext.lower() == '.yaml':
            spec_class = YamlValidatorSpec
        else:
            raise ValueError('Unsupported file type')
        spec = spec_class.load(spec_file)
        return cls(spec, *args, **kwargs)

    def validate(self):
        """Run validation using HTTP requests against validation host

        Using rules provided by spec, perform requests against validation host
        for each rule. Request response is verified to match the spec respsonse
        rule.  This will yield either a :py:cls:`ValidationPass` or
        :py:cls:`ValidationFail` response.
        """
        session = Session()
        if not self.verify:
            urllib3.disable_warnings()
        for rule in self.spec.get_rules():
            req = rule.get_request(self.host, self.port)
            if self.debug:
                pprint.pprint(req.__dict__)
            try:
                resp = session.send(req.prepare(), allow_redirects=False,
                                    verify=self.verify)
                if self.debug:
                    pprint.pprint(resp.__dict__)
                if rule.matches(resp):
                    yield ValidationPass(rule=rule, request=req, response=resp)
            except (ConnectionError, SSLError) as exc:
                # No response yet
                yield ValidationFail(rule=rule, request=req, response=None,
                                     error=exc)
            except ValidationError as exc:
                # Response received, validation error
                yield ValidationFail(rule=rule, request=req, response=resp,
                                     error=exc)


class ValidationResult(object):
    """Base for validation"""

    def __init__(self, rule, request, response, verbose=False):
        self.rule = rule
        self.request = request
        self.response = response
        self.verbose = verbose


class ValidationPass(ValidationResult):
    """Validation pass"""

    pass


class ValidationFail(ValidationResult):

    def __init__(self, rule, request, response, error, verbose=False):
        self.error = error
        super(ValidationFail, self).__init__(rule, request, response, verbose)

    def mismatch(self):
        try:
            (expected, received) = getattr(self.error, 'mismatch')
            return (expected, received)
        except (AttributeError, TypeError, ValueError):
            return None
