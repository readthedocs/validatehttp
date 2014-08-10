# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

from io import StringIO
from unittest import TestCase

from validatehttp.spec import ValidatorSpec, ValidatorSpecRule


class TestSpec(TestCase):

    def setUp(self):
        self.fixtures = [
            '{"http://example.com": {"status_code": 200}}',
            '{"http://example.com/foo/bar": {"status_code": 200}}',
            '{"http://example.com": {"status_code": 200, "method": "post"}}',
            '{"http://example.com": {"request": {"headers": {"x-foo": 42}}}}'
        ]

    def test_spec_load(self):
        spec = ValidatorSpec.load_spec_handle(StringIO(self.fixtures[0]),
                                              spec_format='json')
        assert len(list(spec.get_rules())) == 1

    def test_spec_request_host(self):
        spec = ValidatorSpec.load_spec_handle(StringIO(self.fixtures[0]),
                                              spec_format='json')
        rule = list(spec.get_rules())[0]

        # No host/port
        req = rule.get_request()
        assert req.url == 'http://example.com'
        assert req.method == 'get'
        assert not 'Host' in req.headers
        # Host, no port
        req = rule.get_request(host='0.0.0.0')
        assert req.url == 'http://0.0.0.0'
        assert req.method == 'get'
        assert 'Host' in req.headers
        assert req.headers['Host'] == 'example.com'
        # Host and port
        req = rule.get_request(host='0.0.0.0', port=8000)
        assert req.url == 'http://0.0.0.0:8000'
        assert req.method == 'get'
        assert 'Host' in req.headers
        assert req.headers['Host'] == 'example.com'

    def test_spec_request_path(self):
        spec = ValidatorSpec.load_spec_handle(StringIO(self.fixtures[1]),
                                              spec_format='json')
        rule = list(spec.get_rules())[0]

        # No host/port
        req = rule.get_request()
        assert req.url == 'http://example.com/foo/bar'
        assert req.method == 'get'
        assert not 'Host' in req.headers
        # Host, no port
        req = rule.get_request(host='0.0.0.0')
        assert req.url == 'http://0.0.0.0/foo/bar'
        assert req.method == 'get'
        assert 'Host' in req.headers
        assert req.headers['Host'] == 'example.com'
        # Host and port
        req = rule.get_request(host='0.0.0.0', port=8000)
        assert req.url == 'http://0.0.0.0:8000/foo/bar'
        assert req.method == 'get'
        assert 'Host' in req.headers
        assert req.headers['Host'] == 'example.com'

    def test_spec_request_header(self):
        spec = ValidatorSpec.load_spec_handle(StringIO(self.fixtures[3]),
                                              spec_format='json')
        rule = list(spec.get_rules())[0]

        # No host/port
        req = rule.get_request()
        assert req.url == 'http://example.com'
        assert req.method == 'get'
        assert 'x-foo' in req.headers
        assert req.headers['x-foo'] == 42
