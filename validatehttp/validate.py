# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import urlparse
from collections import namedtuple

from requests import Request, Response, Session

from .spec import ValidatorSpec


class Validator(object):

    def __init__(self, spec, host=None, port=None):
        self.spec = spec
        self.host = host
        self.port = port

    def __repr__(self):
        return '<Validator spec={spec}>'.format(**self.__dict__)

    @classmethod
    def load(cls, spec_file, host=None, port=None):
        spec = ValidatorSpec.load(spec_file)
        return cls(spec, host, port)

    def validate(self):
        session = Session()
        for rule in self.spec.get_rules():
            req = rule.get_request(self.host, self.port)
            resp = session.send(req.prepare(), allow_redirects=False)
            try:
                if rule.matches(resp):
                    yield ValidationPass(rule=rule, request=req, response=resp)
                else:
                    raise Exception('Rule miss without exception')
            except Exception as e:
                yield ValidationFail(rule=rule, request=req, response=resp,
                                     error=e)


ValidationPass = namedtuple('ValidationPass', ['rule', 'request', 'response'],
                            verbose=False)
ValidationFail = namedtuple('ValidationFail',
                            ['rule', 'request', 'response', 'error'],
                            verbose=False)
