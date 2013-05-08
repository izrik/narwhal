#!/usr/bin/env python

from setuptools import setup
import narwhal

setup(
    name='narwhal',
    version=narwhal.__version__,
    packages=['narwhal'],
    license=open('LICENSE').read(),
    long_description=open('README.txt').read(),
    author='Richard Sartor',
    author_email='richard.sartor@rackspace.com',
    url='https://github.com/richard-sartor/narwhal',
    description='Setup scripts for repose',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    install_requires=[
        'requests',
        'argparse',
    ],
    entry_points={
        'console_scripts': [
            'download-repose = narwhal.download_repose:run',
            'run-repose = narwhal.run_repose:run',
            'configure-repose = narwhal.configure_repose:run',
        ],
    }
)
