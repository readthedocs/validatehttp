# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import sys
import os.path
import json
import urlparse
from collections import namedtuple

from requests import Request, Response, Session
from pynag.Plugins import simple as Plugin
try:
    import yaml
except ImportError:
    pass


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

    def run(self):
        self.activate()
        validator = SpecValidator()
        validator.load(self['file'])
        validator.run(host=self['host'], port=self['port'])


class SpecValidator(object):

    def __init__(self):
        self.spec = None

    def load(self, spec_file):
        if self.spec is None:
            if not os.path.exists(spec_file):
                raise IOError('Spec file does not exist')
            (filename, fileext) = os.path.splitext(spec_path)
            handle = open(filename)
            if fileext.lower() == '.json':
                self.load_spec_format(handle, 'json')
            elif fileext.lower() == '.yaml':
                self.load_spec_format(handle, 'yaml')
            else:
                raise Exception("Unsupported file type")
        return self.spec

    def load_spec_format(self, handle, spec_format='json'):
        if spec_format == 'json':
            self.spec = json.load(handle)
        elif spec_format == 'yaml':
            if not 'yaml' in sys.modules:
                raise NameError("YAML support is missing")
            self.spec = yaml.load(handle)
        else:
            raise Exception("Unsupported spec format")

    def run(self, host=None, port=80):
        session = Session()
        for uri in self.spec:
            req_params = {}
            resp_params = {}
            if 'request' in self.spec[uri]:
                req_params = self.spec[uri]['request']
            if 'response' in self.spec[uri]:
                resp_params = self.spec[uri]['response']
            req = self.get_request(uri, req_params, host, port)
            resp = session.send(req.prepare())
            print(resp.headers)
            yield self.compare_response(resp, resp_params)

    def compare_response(self, resp, params):
        # Compare
        if resp.status_code != params['status_code']:
            return False
        if 'headers' in params:
            for (header, value) in params['headers'].items():
                if header in resp.headers:
                    if resp.headers[header] != header.lower():
                        return False
                else:
                    return False
        return True


    def get_request(self, uri, params, host=None, port=80):
        if host is None:
            return Request(params)
        else:
            if not 'headers' in params:
                params['headers'] = {}
            if not 'method' in params:
                params['method'] = 'get'
            parsed_url = urlparse.urlparse(uri)
            replaced_url = parsed_url._replace(
                netloc="{}:{}".format(host, port))
            params['headers']['Host'] = parsed_url.hostname
            return Request(
                url=replaced_url.geturl(),
                **params
            )


def run_plugin():
    plugin = CheckURLSpecPlugin()
    plugin.run()
