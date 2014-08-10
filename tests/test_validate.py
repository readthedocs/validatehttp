# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

from io import StringIO
from unittest import TestCase

from validatehttp.spec import ValidatorSpec
from validatehttp.validate import Validator


class TestSpec(TestCase):

    def test_validator(self):
        validator = Validator.load('rtd.yaml', host='162.209.108.192', port=8000)
        validator.run()
        assert False
