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

requires = ['pyrax>=1.4.7',
            'ipython==1.0.0a',
            'tornado>=3.1',
            'pyzmq>=13.1.0',
            'Jinja2>=2.7',
]

setup(name='ipynb_swiftstore',
      version='0.0.0',
      description='IPython notebook storage for OpenStack Swift',
      author='Kyle Kelley',
      author_email='rgbkrk@gmail.com',
      url='http://github.com/rgbkrk/ipynb-swiftstore',
      py_modules=['ipynb_swiftstore'],
      package_data={'': ['LICENSE']},
      include_package_data=False,
      install_requires=requires,
      # Can't pull from the zip file as IPython uses git submodules
      #dependency_links=["http://1e991763eb16b226de7f-815b705eb00655bf9ca363d7dfb3b606.r62.cf2.rackcdn.com/ipython_fed72595f462ec5a060aa4b5a2b1621e7b682b54.tgz"],
      license=open('LICENSE').read(),
      zip_safe=True,
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

