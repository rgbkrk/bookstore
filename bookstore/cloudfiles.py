#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
A notebook manager that uses Rackspace CloudFiles.

Requires IPython 1.0.0+

Add this to your ipython notebook profile (`ipython_notebook_config.py`):

    c.NotebookApp.notebook_manager_class = 'bookstore.cloudfiles.CloudFilesNotebookManager'
    c.CloudFilesNotebookManager.account_name = USER_NAME
    c.CloudFilesNotebookManager.account_key = API_KEY
    c.CloudFilesNotebookManager.container_name = u'notebooks'

You'll need to replace `USER_NAME` and `API_KEY` with your actual username and
api key of course. You can get the API key from the cloud control panel after logging in.

It's easy to set up a notebook profile if you don't have one:

    $ ipython profile create bookstore
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_bookstore/ipython_config.py'
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_bookstore/ipython_notebook_config.py'

You can also use your default config, located at

~/.ipython/profile_default/ipython_notebook_config.py

"""

#-----------------------------------------------------------------------------
# Copyright (C) 2013 Rackspace
#
# Distributed under the terms of the Apache 2.0 License. The full license is in
# the file LICENSE, distributed as part of this software.
#-----------------------------------------------------------------------------

import pyrax

from tornado import web

from swift import SwiftNotebookManager

from IPython.utils.traitlets import Unicode

class CloudFilesNotebookManager(SwiftNotebookManager):
    '''
    Manages IPython notebooks on Rackspace.

    Rackspace is a known entity (configured OpenStack), so the setup is easier
    than the base OpenStack installation.
    '''

    account_name = Unicode('', config=True, help='Rackspace username')
    account_key = Unicode('', config=True, help='Rackspace API Key')
    region = Unicode('DFW', config=True, help='Region')
    identity_type = "rackspace"

    def __init__(self, **kwargs):
        '''
        Sets up the NotebookManager using the credentials supplied from the
        IPython configuration.
        '''
        super(CloudFilesNotebookManager,self).__init__(**kwargs)
        pyrax.set_setting("identity_type", self.identity_type)
        pyrax.set_setting("region", self.region)

        pyrax.set_credentials(username=self.account_name, api_key=self.account_key)
        self.cf = pyrax.cloudfiles

        self.container = self.cf.create_container(self.container_name)

    def info_string(self):
        '''
        Returns a status string about the Rackspace CloudFiles Notebook Manager
        '''
        info = "Serving {}'s notebooks on Rackspace CloudFiles from container {} in {} region."
        return info.format(self.account_name, self.container_name, self.region)

