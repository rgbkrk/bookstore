#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""A notebook manager that uses Rackspace CloudFiles.

Requires IPython 1.0.0+

Add this to your ipython notebook profile (`ipython_notebook_config.py`):

    c.NotebookApp.notebook_manager_class = 'bookstore.cloudfiles.CloudFilesNotebookManager'
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

You can also use your default config, located at

~/.ipython/profile_default/ipython_notebook_config.py

"""

import pyrax
from IPython.utils.traitlets import Unicode
from .multicloud import LibcloudNotebookManager
from tornado import web


class CloudFilesNotebookManager(LibcloudNotebookManager):
    """Manages IPython notebooks on Rackspace's Cloud.

    Rackspace is a known entity (configured OpenStack), so the setup is
    simplified.
    """

    account_name = Unicode('', config=True, help='Rackspace username')
    account_key = Unicode('', config=True, help='Rackspace API Key')
    region = Unicode('DFW', config=True, help='Region')

    def __init__(self, **kwargs):
        """Sets up the NotebookManager using the credentials supplied from the
        IPython configuration.
        """
        super(CloudFilesNotebookManager, self).__init__(**kwargs)

        self.driver = get_driver(Provider.CLOUDFILES)

        # TODO: Verify the region casing (Is it case sensitive?)
        self.client = driver(self.account_name, self.account_key, self.region)

        # TODO: The next steps should be handled in the parent class
        self.client.connection.user_agent_append(self.user_agent)
        self.container = self.client.get_container(self.container_name)

    def info_string(self):
        """Returns a status string about the Rackspace CloudFiles Notebook
        Manager
        """
        info = ("Serving {}'s notebooks on Rackspace CloudFiles from "
                "container {} in the {} region.")
        return info.format(self.account_name, self.container_name, self.region)
