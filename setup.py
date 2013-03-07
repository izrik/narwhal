#!/usr/bin/env python

from setuptools import setup

setup(
    name='narwhal',
    version='0.1.1',
    packages=['narwhal',],
    license='MIT License',
    long_description=open('README.txt').read(),
    author='Richard Sartor',
    author_email='richard.sartor@rackspace.com',
    url='https://github.com/richard-sartor/narwhal',
    description='Setup scripts for repose',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    install_requires=[
        'requests',
        'argparse',
        'pushy',
        'pyrax',
        'paramiko',
    ],
)
