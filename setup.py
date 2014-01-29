from setuptools import setup

setup(
    # http://pythonhosted.org/setuptools/setuptools.html
    name='smsframework',
    version='0.0.2',
    author='Mark Vartanyan',
    author_email='kolypto@gmail.com',

    url='https://github.com/kolypto/py-smsframework',
    license='MIT',
    description="Bi-directional SMS gateway with pluggable providers",
    long_description=open('README.rst').read(),
    keywords=['sms', 'message', 'notification', 'receive', 'send'],

    packages=['smsframework'],
    scripts=[],

    install_requires=[
    ],
    extras_require={
        'clickatell': ['smsframework-clickatell >= 0.0.1'],
        'receiver': ['flask >= 0.10']
    },
    include_package_data=True,

    platforms='any',
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
)
