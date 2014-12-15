'''HTTP validator spec object representation'''

# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os.path
import json
import sys
import urlparse

from requests import Request, Response
try:
    import yaml
except ImportError:
    pass


class ValidatorSpecBase(object):
    '''List of validator spec rules'''

    def __init__(self, rules):
        self.rules = rules

    @classmethod
    def load(cls, spec_file):
        '''Load from spec file'''
        if not os.path.exists(spec_file):
            raise IOError('Spec file does not exist')
        handle = open(spec_file)
        rules = []
        spec = cls.parse(handle)
        for (uri, params) in spec.items():
            try:
                rules.append(ValidatorSpecRule(uri, **params))
            except KeyError:
                pass
        return cls(rules)

    @classmethod
    def parse(cls, handle):
        raise NotImplemented()

    def get_rules(self):
        '''Yield rules with proper request object'''
        for rule in self.rules:
            yield rule


class JsonValidatorSpec(ValidatorSpecBase):

    @classmethod
    def parse(cls, handle):
        try:
            spec = json.load(handle)
        except ValueError:
            raise ValueError("Invalid JSON spec file")
        return spec


class YamlValidatorSpec(ValidatorSpecBase):

    @classmethod
    def parse(cls, handle):
        if not 'yaml' in sys.modules:
            raise NameError("YAML support is missing")
        try:
            spec = yaml.safe_load(handle.read())
        except ValueError:
            raise ValueError("Invalid YAML spec file")
        return spec


class ValidatorSpecRule(object):
    '''Validator spec rule'''

    def __init__(self, uri, request=None, **response):
        self.uri = uri

        # Normalize request
        if request is None:
            request = {}
        if not 'headers' in request:
            request['headers'] = {}
        if not 'method' in request:
            request['method'] = 'get'
        self.request = request

        if response is None:
            response = {}
        if not 'headers' in response:
            response['headers'] = {}
        self.response = response

    def __repr__(self):
        return "<ValidatorSpecRule uri={uri}>".format(**self.__dict__)

    def get_request(self, host=None, port=None):
        '''Creat HTTP request from host/port and request params

        :param host: Host address
        :param port: Host port
        '''
        # Replace network location chunk of URI so that we can hit separate
        # web servers with the same spec file
        params = self.request
        parsed_url = urlparse.urlparse(self.uri)
        if host is None and port is None:
            params['url'] = self.uri
            return Request(**params)
        elif host is not None and port is not None:
            replaced_url = parsed_url._replace(
                netloc="{}:{}".format(host, port))
            params['url'] = replaced_url.geturl()
        elif host is not None and port is None:
            replaced_url = parsed_url._replace(netloc=host)
            params['url'] = replaced_url.geturl()
        elif host is None and port is not None:
            raise Exception('Host or host and port must be specified')

        # Add host header with original hostname and return Request object
        params['headers']['Host'] = parsed_url.hostname
        return Request(**params)

    def matches(self, resp):
        '''Test whether HTTP response matches defined rule response

        Returns True on a match, otherwise raise :py:cls:`ValueError` on a
        mismatch.

        :param resp: HTTP response object from request
        :type resp: Response
        '''
        if isinstance(resp, Response):
            params = self.response
            for (key, value) in params.items():
                if key == 'headers':
                    for (header, value) in params.get('headers').items():
                        resp_value = resp.headers.get(header)
                        if resp_value != value:
                            raise ValueError(
                                'Response header {0} mismatch ({1} != {2})'
                                .format(header, value, resp_value))
                else:
                    resp_value = getattr(resp, key, None)
                    if resp_value != value:
                        raise ValueError(
                            'Response {0} mismatch ({1} != {2})'
                            .format(key, value, resp_value))
        return True
