#! /usr/bin/env python
""" Bi-directional SMS gateway with pluggable providers """

from setuptools import setup, find_packages

setup(
    # http://pythonhosted.org/setuptools/setuptools.html
    name='smsframework',
    version='0.0.9-3',
    author='Mark Vartanyan',
    author_email='kolypto@gmail.com',

    url='https://github.com/kolypto/py-smsframework',
    license='BSD',
    description=__doc__,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords=['sms', 'message', 'notification', 'receive', 'send'],

    packages=find_packages(),
    scripts=[],
    entry_points={},

    install_requires=[],
    extras_require={
        'clickatell': ['smsframework-clickatell >= 0.0.3'],
        'vianett': ['smsframework-vianett >= 0.0.2'],
        'receiver': ['flask >= 0.10'],
        'async': ['asynctools >= 0.1.3'],
    },
    include_package_data=True,
    test_suite='nose.collector',

    platforms='any',
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
