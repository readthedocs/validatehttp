'''Nagios checkurlspec plugin

Using a spec file in JSON or YAML, check a given host for response code and
header returns
'''

from setuptools import setup, find_packages

setup(
    name='nagios-checkurlspec',
    version=0.1,
    description='Nagios plugin to check a spec file of URL responses',
    long_description=__doc__,
    keywords='nagios url',
    author='Anthony Johnson',
    author_email='aj@ohess.org',
    license='MIT',
    packages=find_packages(),
    install_requires=['pynag'],
    tests_require=['nose'],
    test_suite='nose.collector',
    entry_points = {
        'console_scripts': ['check_urlspec=checkurlspec:run_plugin'],
    }
)
