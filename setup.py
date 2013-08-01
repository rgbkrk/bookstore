#!/usr/bin/env python

# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('requirements.txt') as reqs:
    requires = reqs.read().splitlines()

setup(name='bookstore',
      version='0.0.0',
      description='Stores IPython notebooks to cloud storage providers including OpenStack Swift and Rackspace CloudFiles',
      author='Kyle Kelley',
      author_email='rgbkrk@gmail.com',
      url='http://github.com/rgbkrk/bookstore',
      packages = ['bookstore'],
      package_data={'': ['LICENSE']},
      include_package_data=False,
      install_requires=requires,
      dependency_links=['http://archive.ipython.org/testing/1.0.0/ipython-1.0.0a1.tar.gz#egg=ipython-1.0.0a1'],
      license=open('LICENSE').read(),
      classifiers=(
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Environment :: OpenStack',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Distributed Computing',
      ),
)

