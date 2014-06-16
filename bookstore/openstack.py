#!/usr/bin/env python

# -*- coding: utf-8 -*-

import os
from IPython.utils.traitlets import Unicode
from . import SwiftNotebookManager


class OpenStackNotebookManager(SwiftNotebookManager):

    auth_url = Unicode(
        os.getenv('OS_AUTH_URL', ''), config=True,
        help='OpenStack auth URL. Defaults to env[OS_AUTH_URL].'
    )

    user_name = Unicode(
        os.getenv('OS_USERNAME', ''), config=True,
        help='OpenStack username. Defaults to env[OS_USERNAME].'
    )

    password = Unicode(
        os.getenv('OS_PASSWORD', ''), config=True,
        help='OpenStack password. Defaults to env[OS_PASSWORD].'
    )

    tenant_id = Unicode(
        os.getenv('OS_TENANT_ID', ''), config=True,
        help='OpenStack tenant ID. Defaults to env[OS_TENANT_ID].'
    )

    tenant_name = Unicode(
        os.getenv('OS_TENANT_NAME', ''), config=True,
        help='OpenStack tenant name. Defaults to env[OS_TENANT_NAME].'
    )

    def __init__(self, **kwargs):
        super(OpenStackNotebookManager, self).__init__(**kwargs)
        self.connection_args = {
            'authurl': self.auth_url,
            'user': self.user_name,
            'key': self.password,
            'auth_version': 2,
            'os_options': {
                'tenant_name': self.tenant_name,
                'tenant_id': self.tenant_id
            }
        }
