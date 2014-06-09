#!/usr/bin/env python

# -*- coding: utf-8 -*-

import os
import sys

import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Backwards compatibility for Python 2.x
try:
    from itertools import ifilter
    filter = ifilter
except ImportError:
    pass


def get_version():
    '''
    Version slurping without importing bookstore, since dependencies may not be
    met until setup is run.
    '''
    version_regex = re.compile(r"__version__\s+=\s+"
                               r"['\"](\d+.\d+.\d+\w*)['\"]$")
    versions = filter(version_regex.match, open("bookstore/__init__.py"))

    try:
        version = next(versions)
    except StopIteration:
        raise Exception("Bookstore version not set")

    return version_regex.match(version).group(1)

version = get_version()

# Utility for publishing the bookstore, courtesy kennethreitz/requests
if sys.argv[-1] == 'publish':
    print("Publishing bookstore {version}".format(version=version))
    os.system('python setup.py sdist upload')
    sys.exit()

packages = ['bookstore']
requires = []

with open('requirements.txt') as reqs:
    requires = reqs.read().splitlines()

setup(name='bookstore',
      version=version,
      description='IPython notebook storage on OpenStack Swift + Rackspace.',
      long_description=open('README.rst').read(),
      author='Kyle Kelley',
      author_email='rgbkrk@gmail.com',
      url='http://github.com/rgbkrk/bookstore',
      packages=packages,
      package_data={'': ['LICENSE']},
      include_package_data=False,
      install_requires=requires,
      license=open('LICENSE').read(),
      zip_safe=False,
      classifiers=(
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Framework :: IPython',
          'Environment :: OpenStack',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Distributed Computing',
      ),
      )
