"""
Test validation spec and spec rule creation
"""

# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from unittest import TestCase

from mock import mock_open
from mock import patch

from validatehttp.spec import JsonValidatorSpec
from validatehttp.validate import Validator


class TestSpec(TestCase):
    def setUp(self):
        self.fixtures = [
            '{"http://example.com": {"status_code": 200}}',
            '{"http://example.com/foo/bar": {"status_code": 200}}',
            '{"http://example.com": {"status_code": 200, "method": "post"}}',
            '{"http://example.com": {"request": {"headers": {"x-foo": 42}}}}',
            '{"foo": FAIL HERE}',
        ]

    # JSON support
    @patch("os.path.exists", lambda n: True)
    @patch("validatehttp.spec.open", create=True)
    def test_load_json_from_file(self, mock):
        """Load json from mocked file"""
        mock_open(mock, read_data=self.fixtures[0])
        validator = Validator.load("rtd.json", host="127.0.0.1", port=8000)
        self.assertEqual(len(list(validator.spec.get_rules())), 1)

    @patch("os.path.exists", lambda n: True)
    @patch("validatehttp.spec.open", create=True)
    def test_invalid_json_from_file(self, mock):
        """Invalid json from mocked file"""
        mock_open(mock, read_data=self.fixtures[4])
        self.assertRaises(ValueError, Validator.load, "rtd.json")

    # YAML support
    @patch("os.path.exists", lambda n: True)
    @patch("validatehttp.spec.open", create=True)
    def test_yaml_not_loaded(self, mock):
        """YAML is not loaded"""
        import sys

        mock_open(mock, read_data="foo: status_code: 200")
        with patch.dict("sys.modules", yaml=None):
            del sys.modules["yaml"]
            self.assertRaises(NameError, Validator.load, "rtd.yaml")

    @patch("os.path.exists", lambda n: True)
    @patch("validatehttp.spec.open", create=True)
    def test_invalid_yaml_from_file(self, mock):
        """Invalid YAML from mocked file"""
        mock_open(mock, read_data="foo: status_code: tr")
        self.assertRaises(ValueError, Validator.load, "rtd.yaml")

    # Generic
    @patch("os.path.exists", lambda n: True)
    @patch("validatehttp.spec.open", create=True)
    def test_bad_spec(self, mock):
        """Valid data, but bad spec"""
        mock_open(mock, read_data="foo:")
        validator = Validator.load("rtd.yaml", host="127.0.0.1", port=8000)
        self.assertEqual(len(list(validator.spec.get_rules())), 0)

    @patch("os.path.exists", lambda n: True)
    @patch("validatehttp.spec.open", create=True)
    def test_spec_request_host(self, mock):
        """Compare spec rules"""
        mock_open(mock, read_data=self.fixtures[0])
        validator = Validator.load("rtd.json", host="127.0.0.1", port=8000)
        rule = list(validator.spec.get_rules())[0]

        # No host/port
        req = rule.get_request()
        assert req.url == "http://example.com"
        assert req.method == "get"
        assert "Host" not in req.headers
        # Host, no port
        req = rule.get_request(host="0.0.0.0")
        assert req.url == "http://0.0.0.0"
        assert req.method == "get"
        assert "Host" in req.headers
        assert req.headers["Host"] == "example.com"
        # Host and port
        req = rule.get_request(host="0.0.0.0", port=8000)
        assert req.url == "http://0.0.0.0:8000"
        assert req.method == "get"
        assert "Host" in req.headers
        assert req.headers["Host"] == "example.com"

    @patch("os.path.exists", lambda n: True)
    @patch("validatehttp.spec.open", create=True)
    def test_spec_request_path(self, mock):
        """Test URL and path construction"""
        mock_open(mock, read_data=self.fixtures[1])
        spec = JsonValidatorSpec.load("test.json")
        rule = list(spec.get_rules())[0]

        # No host/port
        req = rule.get_request()
        assert req.url == "http://example.com/foo/bar"
        assert req.method == "get"
        assert "Host" not in req.headers
        # Host, no port
        req = rule.get_request(host="0.0.0.0")
        assert req.url == "http://0.0.0.0/foo/bar"
        assert req.method == "get"
        assert "Host" in req.headers
        assert req.headers["Host"] == "example.com"
        # Host and port
        req = rule.get_request(host="0.0.0.0", port=8000)
        assert req.url == "http://0.0.0.0:8000/foo/bar"
        assert req.method == "get"
        assert "Host" in req.headers
        assert req.headers["Host"] == "example.com"

    @patch("os.path.exists", lambda n: True)
    @patch("validatehttp.spec.open", create=True)
    def test_spec_request_header(self, mock):
        """Test request with headers"""
        mock_open(mock, read_data=self.fixtures[3])
        spec = JsonValidatorSpec.load("test.json")
        rule = list(spec.get_rules())[0]

        # No host/port
        req = rule.get_request()
        assert req.url == "http://example.com"
        assert req.method == "get"
        assert "x-foo" in req.headers
        assert req.headers["x-foo"] == 42
