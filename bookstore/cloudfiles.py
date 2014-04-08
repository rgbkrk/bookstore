#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
"""

from IPython.utils.traitlets import Unicode
from .keystone import SwiftNotebookManager
import swiftclient

class CloudFilesNotebookManager(SwiftNotebookManager):
    """
    A notebook manager that uses Rackspace CloudFiles.

    Requires IPython 2.0+

    Add this to your ipython notebook profile (`ipython_notebook_config.py`):

        c.NotebookApp.notebook_manager_class = 'bookstore.CloudFilesNotebookManager'
        c.CloudFilesNotebookManager.account_name = USER_NAME
        c.CloudFilesNotebookManager.account_key = API_KEY
        c.CloudFilesNotebookManager.container_name = u'notebooks'

    You'll need to replace `USER_NAME` and `API_KEY` with your actual username and
    api key of course. You can get the API key from the cloud control panel after
    logging in.

    It's easy to set up a notebook profile if you don't have one:

        $ ipython profile create bookstore
        [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_bookstore/ipython_config.py'
        [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_bookstore/ipython_notebook_config.py'
    """

    account_name = Unicode('', config=True, help='Rackspace username')
    account_key = Unicode('', config=True, help='Rackspace API Key')
    region = Unicode('DFW', config=True, help='Region')
    auth_endpoint = Unicode('https://identity.api.rackspacecloud.com/v2.0/', config=True, help='Authentication endpoint.')
    tenant_name = Unicode(
        ' ', config=True, help='The tenant name used for authentication')

    def __init__(self, **kwargs):
        """Sets up the NotebookManager using the credentials supplied from the
        IPython configuration.
        """
        super(CloudFilesNotebookManager, self).__init__(**kwargs)

        # FIXME
        # this is not how rackspace works, see
        # http://docs.rackspace.com/files/api/v1/cf-devguide/content/Retrieving_Auth_Token.html

        connection = swiftclient.Connection(authurl=self.auth_endpoint,
                                            user=self.account_name, key=self.account_key,
                                            tenant_name=self.tenant_name,
                                            auth_version='2')

        self.connection = connection
        connection.put_container(self.container)

    def info_string(self):
        """Returns a status string about the Rackspace CloudFiles Notebook
        Manager
        """
        info = ("Serving {}'s notebooks on Rackspace CloudFiles from "
                "container {} in the {} region.")
        return info.format(self.account_name, self.container_name, self.region)
