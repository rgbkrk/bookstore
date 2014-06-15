#!/usr/bin/env python

# -*- coding: utf-8 -*-
'''Bookstore

Stores IPython notebooks automagically onto OpenStack clouds through Swift.
'''

__title__ = 'bookstore'
__version__ = '1.0.0'
__build__ = 0x010000
__author__ = 'Kyle Kelley'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2013 Kyle Kelley'

from IPython.utils.traitlets import Unicode, TraitError
import swiftclient
from .swift import SwiftNotebookManager

class CloudFilesNotebookManager(SwiftNotebookManager):

    auth_endpoint = Unicode('https://identity.api.rackspacecloud.com/v2.0/',
                            config=True, help='Authentication endpoint.')

    account_name = Unicode('', config=True,
                           help='Rackspace username.')

    account_key = Unicode('', config=True,
                          help='Rackspace password.')

    tenant_name = Unicode('', config=True,
                          help='Rackspace tenant (optional)')
