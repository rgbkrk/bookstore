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

# When IPython 1.0 releases, this will become packaged for real. For now this
# just includes the basic requirements for the package. IPython should be
# installed using git:
#
# pip install -e git+https://github.com/ipython/ipython.git@0741b515e0142e3e1e8639294e800576ac2b4a04#egg=ipython
#
#
requires = [
        'pyrax==1.4.7',
]

#with open('requirements.txt') as reqs:
#    requires = reqs.read().splitlines()

setup(name='bookstore',
      version='0.0.0',
      description='IPython notebook manager for OpenStack Swift and Rackspace',
      author='Kyle Kelley',
      author_email='rgbkrk@gmail.com',
      url='http://github.com/rgbkrk/bookstore',
      packages = ['bookstore'],
      package_data={'': ['LICENSE']},
      include_package_data=False,
      install_requires=requires,
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

