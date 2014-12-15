# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

from io import StringIO
from unittest import TestCase

from mock import patch, mock_open
from requests import Response
from requests.exceptions import SSLError, ConnectionError

from validatehttp.spec import YamlValidatorSpec, ValidatorSpecRule
from validatehttp.validate import Validator, ValidationPass, ValidationFail


class TestValidator(TestCase):

    @patch('os.path.exists', lambda n: False)
    @patch('validatehttp.spec.open', create=True)
    def test_missing_file(self, mock):
        '''Fail on missing file'''
        mock_open(mock, read_data='{"/foo": {"status_code": 200}}')
        self.assertRaises(IOError, Validator.load, 'test.json')

    @patch('os.path.exists', lambda n: True)
    @patch('validatehttp.spec.open', create=True)
    def test_load_json(self, mock):
        '''Pass loading JSON file'''
        mock_open(mock, read_data='{"/foo": {"status_code": 200}}')
        validator = Validator.load('test.json')
        self.assertEqual(len(list(validator.spec.get_rules())), 1)

    @patch('os.path.exists', lambda n: True)
    @patch('validatehttp.spec.open', create=True)
    def test_load_yaml(self, mock):
        '''Pass loading YAML file'''
        mock_open(mock, read_data=("foo:\n"
                                   "  status_code: 200\n"))
        validator = Validator.load('test.yaml')
        self.assertEqual(len(list(validator.spec.get_rules())), 1)

    @patch('os.path.exists', lambda n: True)
    @patch('validatehttp.spec.open', create=True)
    def test_load_unknown(self, mock):
        '''Fail on unknown file extension'''
        mock_open(mock, read_data="None")
        self.assertRaises(ValueError, Validator.load, 'test.foo')


class TestValidatorValidation(TestCase):

    def setUp(self):
        self.validator = Validator('test.yaml', host='127.0.0.1', port=80)
        self.validator.spec = YamlValidatorSpec([
            ValidatorSpecRule(
                'http://example.com',
                status_code=200,
                headers={'x-test': 'foobar'}
            )])

    def assertRuleMatches(self, result, passing=True, error=None):
        if passing:
            self.assertIsInstance(result, ValidationPass)
        else:
            self.assertIsInstance(result, ValidationFail)
        if error is not None:
            self.assertRegexpMatches(str(result.error), error)

    @patch('validatehttp.validate.Session.send')
    def test_response_match(self, mock):
        '''Vanilla response with headers matches rule'''
        mock.return_value = Response()
        mock.return_value.status_code = 200
        mock.return_value.headers = {'x-test': 'foobar'}
        for result in self.validator.validate():
            self.assertRuleMatches(result, passing=True)

    @patch('validatehttp.validate.Session.send')
    def test_response_status_mismatch(self, mock):
        '''Response status code doesn't match'''
        mock.return_value = Response()
        mock.return_value.status_code = 400
        mock.return_value.headers = {'x-test': 'foobar'}
        for result in self.validator.validate():
            self.assertRuleMatches(result, passing=False,
                                   error=r'status_code mismatch')

    @patch('validatehttp.validate.Session.send')
    def test_response_header_mismatch(self, mock):
        '''Response header is missing or doesn't match'''
        mock.return_value = Response()
        mock.return_value.status_code = 200
        mock.return_value.headers = {'x-nonexistant': 'foobar'}
        for result in self.validator.validate():
            self.assertRuleMatches(result, passing=False,
                                   error=r'header x-test mismatch')
        mock.return_value.headers = {'x-test': 'do not match'}
        for result in self.validator.validate():
            self.assertRuleMatches(result, passing=False,
                                   error=r'header x-test mismatch')

    @patch('validatehttp.validate.Session.send')
    def test_connection_error(self, mock):
        '''Test connection error throws a validation error'''
        def _raise(*args, **kwargs):
            raise ConnectionError('Connection error')
        mock.side_effect = _raise
        results = list(self.validator.validate())
        self.assertRuleMatches(results[0], passing=False, error=r'Connection')

    @patch('validatehttp.validate.Session.send')
    def test_ssl_error(self, mock):
        '''Test ssl error response'''
        def _raise(*args, **kwargs):
            raise SSLError('SSL error')
        mock.side_effect = _raise
        results = list(self.validator.validate())
        self.assertRuleMatches(results[0], passing=False, error=r'SSL')
