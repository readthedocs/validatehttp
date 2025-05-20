'''
validatehttp - HTTP request spec validation
===========================================

Using a spec file in JSON or YAML, run requests
'''

from setuptools import setup, find_packages

setup(
    name='validatehttp',
    version=0.2,
    description='Validate a list of HTTP request spec against a host',
    long_description=__doc__,
    keywords='nagios url',
    author='Anthony Johnson',
    author_email='aj@ohess.org',
    license='MIT',
    packages=find_packages(),
    install_requires=['requests', 'pyyaml', 'termcolor'],
    extras_require={
        'Nagios': ['pynag'],
    },
    tests_require=['pytest', 'mock', 'pyyaml'],
    test_suite='nose.collector',
    entry_points = {
        'console_scripts': [
            'check_validatehttp=validatehttp.nagios:CheckURLSpecPlugin.run',
            'validatehttp=validatehttp.cli:ValidatorCLI.cli'
        ],
    }
)
