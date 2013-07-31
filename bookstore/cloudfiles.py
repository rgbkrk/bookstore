#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
A notebook manager that uses OpenStack Swift object storage.

ipynb_swiftstore requires IPython 1.0.0a or greater to work.

To use this with IPython, you'll need IPython notebook fully installed
(ipython, tornado, pyzmq, and Jinja2) and a notebook profile.

It's easy to set up a notebook profile if you don't have one:

    $ ipython profile create swifty_ipy
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_swiftstore/ipython_config.py'
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_swiftstore/ipython_notebook_config.py'

Now, add this to your ipython notebook profile (`ipython_notebook_config.py`):

    c.NotebookApp.notebook_manager_class = 'ipynb_swiftstore.OpenStackNotebookManager'
    c.OpenStackNotebookManager.account_name = USER_NAME
    c.OpenStackNotebookManager.account_key = API_KEY
    c.OpenStackNotebookManager.container_name = u'notebooks'
    c.OpenStackNotebookManager.identity_type = u'rackspace' #keystone for other OpenStack implementations
    c.OpenStackNotebookManager.auth_endpoint = u'' #

You'll need to replace `USER_NAME` and `API_KEY` with your actual username and
api key of course. You can get the API key from the cloud control panel after logging in.

"""

#-----------------------------------------------------------------------------
# Copyright (C) 2013 Rackspace
#
# Distributed under the terms of the Apache 2.0 License. The full license is in
# the file LICENSE, distributed as part of this software.
#-----------------------------------------------------------------------------

import datetime

import pyrax
from pyrax.exceptions import NoSuchContainer

from tornado import web

from IPython.html.services.notebooks.nbmanager import NotebookManager

from IPython.nbformat import current
from IPython.utils.traitlets import Unicode, Instance
from IPython.utils.tz import utcnow

METADATA_NBNAME = 'x-object-meta-nbname'

class CloudFilesNotebookManager(SwiftNotebookManager):
    '''
    Manages IPython notebooks on Rackspace.

    Rackspace is a known entity (configured OpenStack), so the setup is easier
    than the base OpenStack installation.
    '''

    account_name = Unicode('', config=True, help='Rackspace username')
    account_key = Unicode('', config=True, help='Rackspace API Key')
    container_name = Unicode('', config=True, help='Container name for notebooks.')

    # TODO: Add optional region

    def __init__(self, **kwargs):
        NotebookManager.__init__(**kwargs)
        #super(CloudFilesNotebookManager, self).__init__(**kwargs)
        pyrax.set_setting("identity_type", "rackspace")
        # Set the region, optionally
        # pyrax.set_setting("region", region) # e.g. "LON"

        pyrax.set_credentials(username=self.account_name, api_key=self.account_key)
        self.cf = pyrax.cloudfiles

        try:
            self.container = self.cf.get_container(self.container_name)
        except NoSuchContainer:
            self.container = self.cf.create_container(self.container_name)
