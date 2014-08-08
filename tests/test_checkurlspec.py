# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

from io import StringIO

from checkurlspec import CheckURLSpecPlugin, SpecValidator


fixture = """
http://readthedocs.org:
    request:
        headers:
            x-something: true
    response:
        status_code: 200
        headers:
            x-perl-redirect: true
http://autotest.readthedocs.org/:
    response:
        status_code: 200
        headers:
            x-perl-redirect: true
"""


def test_requests_run():
    validator = SpecValidator()
    validator.load_spec_format(StringIO(fixture), spec_format='yaml')
    for x in validator.run(host='readthedocs.org', port=80):
        print(x)
    assert False
