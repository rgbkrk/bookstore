#!/usr/bin/env python

# -*- coding: utf-8 -*-

from IPython.utils.traitlets import Unicode
from .swift import SwiftNotebookManager
import swiftclient

class KeystoneNotebookManager(SwiftNotebookManager):
    """
    A notebook manager that uses OpenStack Swift object storage, using Keystone
    authentication

    Requires IPython 2.0+

    Add this to your ipython notebook profile (`ipython_notebook_config.py`),
    filling in details for your OpenStack implementation.

        c.NotebookApp.notebook_manager_class = 'bookstore.KeystoneNotebookManager'

        # Set your user name and API Key
        c.KeystoneNotebookManager.auth_endpoint = OS_AUTH_URL
        c.KeystoneNotebookManager.account_name = OS_USERNAME
        c.KeystoneNotebookManager.account_key = OS_PASSWORD
        c.KeystoneNotebookManager.tenant_name = OS_TENANT_NAME
        c.KeystoneNotebookManager.container_name = u'notebooks'

    It's easy to set up a notebook profile if you don't have one:

        $ ipython profile create swiftstore
        [ProfileCreate] Generating default config file: '/Users/theuser/.ipython/profile_swiftstore/ipython_config.py'
        [ProfileCreate] Generating default config file: '/Users/theuser/.ipython/profile_swiftstore/ipython_notebook_config.py'
    """

    account_name = Unicode('', config=True, help='OpenStack account name.')
    account_key = Unicode('', config=True, help='OpenStack account key.')
    auth_endpoint = Unicode('', config=True, help='Authentication endpoint.')
    tenant_name = Unicode(
        '', config=True, help='The tenant name used for authentication')

    def __init__(self, **kwargs):
        super(SwiftNotebookManager, self).__init__(**kwargs)

        connection = swiftclient.Connection(authurl=self.auth_endpoint,
                                            user=self.account_name, key=self.account_key,
                                            tenant_name=self.tenant_name,
                                            auth_version='2')

        self.connection = connection
        connection.put_container(self.container)
