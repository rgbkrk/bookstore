#!/usr/bin/env python

# -*- coding: utf-8 -*-

from IPython.utils.traitlets import Unicode
from . import SwiftNotebookManager


class CloudFilesNotebookManager(SwiftNotebookManager):

    user_name = Unicode('', config=True,
                        help='CloudFiles username.')

    password = Unicode('', config=True,
                       help='CloudFiles password.')

    auth_url = Unicode('https://identity.api.rackspacecloud.com/v2.0/',
                       config=True, help='Rackspace authentication endpoint.')

    def __init__(self, **kwargs):
        super(CloudFilesNotebookManager, self).__init__(**kwargs)
        self.connection_args = {
            'authurl': self.auth_url,
            'user': self.user_name,
            'key': self.password,
            'auth_version': 2,
            'tenant_name': '',
            'os_options': {
                'tenant_name': '',
            }
        }
