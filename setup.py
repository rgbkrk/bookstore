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
            #'ipython==1.0.0a',
            'tornado>=3.1',
            'pyzmq>=13.1.0',
            'Jinja2>=2.7',
]

setup(name='bookstore',
      version='0.0.0',
      description='IPython notebook manager for OpenStack Swift and Rackspace',
      author='Kyle Kelley',
      author_email='rgbkrk@gmail.com',
      url='http://github.com/rgbkrk/ipynb-swiftstore',
      packages = ['bookstore'],
      package_data={'': ['LICENSE']},
      include_package_data=False,
      install_requires=requires,
      # Can't pull from the zip file as IPython uses git submodules
      #dependency_links=['-e git+https://github.com/ipython/ipython.git@55dfcbc98cd2f1e2bfc6c9f127c97a746f79c459#egg=ipython'],
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

