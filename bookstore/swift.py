#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
A notebook manager that uses OpenStack Swift object storage.

Requires IPython 1.0.0+

Add this to your ipython notebook profile (`ipython_notebook_config.py`),
filling in details for your OpenStack implementation.

    c.NotebookApp.notebook_manager_class = 'bookstore.swift.KeystoneNotebookManager'
    c.KeystoneNotebookManager.account_name = USER_NAME
    c.KeystoneNotebookManager.account_key = API_KEY
    c.KeystoneNotebookManager.container_name = u'notebooks'
    c.KeystoneNotebookManager.auth_endpoint = u'127.0.0.1:8021'
    c.KeystoneNotebookManager.tenant_id = TENANT_ID
    c.KeystoneNotebookManager.tenant_name = TENANT_NAME
    c.KeystoneNotebookManager.region = 'RegionOne'

It's easy to set up a notebook profile if you don't have one:

    $ ipython profile create swiftstore
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_swiftstore/ipython_config.py'
    [ProfileCreate] Generating default config file: u'/Users/theuser/.ipython/profile_swiftstore/ipython_notebook_config.py'

You can also use your default config, located at

~/.ipython/profile_default/ipython_notebook_config.py

"""

#-----------------------------------------------------------------------------
# Copyright (C) 2013 Rackspace
#
# Distributed under the terms of the Apache 2.0 License. The full license is in
# the file LICENSE, distributed as part of this software.
#-----------------------------------------------------------------------------

from datetime import datetime

import pyrax
from pyrax.exceptions import NoSuchContainer

from tornado import web

from IPython.html.services.notebooks.nbmanager import NotebookManager

from IPython.nbformat import current
from IPython.utils.traitlets import Unicode
from IPython.utils.tz import utcnow

from bookstore import __version__

METADATA_NBNAME = 'x-object-meta-nbname'
METADATA_CHK_ID = 'x-object-meta-checkpoint-id'
METADATA_LAST_MODIFIED = 'x-object-meta-nb-last-modified'
METADATA_NB_ID = 'x-object-meta-notebook-id'

DATE_FORMAT = "%X-%x"

class SwiftNotebookManager(NotebookManager):
    '''
    This is a base class to be subclassed by OpenStack providers. The swift
    object storage should work across implementations. The big difference is
    authentication which is implemented separately in
    KeystoneAuthNotebookManager and CloudFilesNotebookManager.
    '''

    user_agent = "bookstore v{version}".format(version=__version__)
    container_name = Unicode('notebooks', config=True, help='Container name for notebooks.')

    def __init__(self, **kwargs):
        super(SwiftNotebookManager, self).__init__(**kwargs)
        pyrax.set_setting("custom_user_agent", self.user_agent)

        # A dictionary mapping notebook ids to lists of checkpoints
        self.next_checkpoint = {}

    def load_notebook_names(self):
        """On startup load the notebook ids and names from OpenStack Swift.

        The object names are the notebook ids and the notebook names are stored
        as object metadata.
        """
        # Cached version of the mapping of notebook IDs to notebook names
        self.mapping = {}

        objects = self.container.get_objects()

        for obj in objects:
            nb_id = obj.name
            metadata = obj.get_metadata()

            name = metadata[METADATA_NBNAME]
            self.mapping[nb_id] = name

    def list_notebooks(self):
        """List all notebooks in the container.

        This version uses `self.mapping` as the authoritative notebook list.
        """
        data = [dict(notebook_id=nb_id,name=name) for nb_id, name in self.mapping.items()]
        data = sorted(data, key=lambda item: item['name'])
        return data

    def read_notebook_object(self, notebook_id):
        '''
        Get the object representation of a notebook by notebook_id.
        '''
        if not self.notebook_exists(notebook_id):
            raise web.HTTPError(404, u'Notebook does not exist: %s' % notebook_id)
        try:
            obj = self.container.get_object(notebook_id)
            s = obj.get() # Read the file into s
        except:
            raise web.HTTPError(500, u'Notebook cannot be read.')
        try:
            nb = current.reads(s, u'json')
        except:
            raise web.HTTPError(500, u'Unreadable JSON notebook.')
        # Todo: The last modified should actually be saved in the notebook document.
        # We are just using the current datetime until that is implemented.
        last_modified = utcnow()
        return last_modified, nb

    def write_notebook_object(self, nb, notebook_id=None):
        '''
        Save an existing notebook object by notebook_id.
        '''

        try:
            new_name = nb.metadata.name
        except AttributeError:
            raise web.HTTPError(400, u'Missing notebook name')

        if notebook_id is None:
            notebook_id = self.new_notebook_id(new_name)

        if notebook_id not in self.mapping:
            raise web.HTTPError(404, u'Notebook does not exist: %s' % notebook_id)

        try:
            data = current.writes(nb, u'json')
        except Exception as e:
            raise web.HTTPError(400, u'Unexpected error while saving notebook: %s' % e)

        metadata = {METADATA_NBNAME: new_name}
        try:
            obj = self.container.store_object(notebook_id, data)
            obj.set_metadata(metadata)
        except Exception as e:
            raise web.HTTPError(400, u'Unexpected error while saving notebook: %s' % e)

        self.mapping[notebook_id] = new_name
        return notebook_id

    def delete_notebook(self, notebook_id):
        '''
        Delete notebook by notebook_id.
        '''
        if not self.notebook_exists(notebook_id):
            raise web.HTTPError(404, u'Notebook does not exist: %s' % notebook_id)
        try:
            self.container.delete_object(notebook_id)
        except Exception as e:
            raise web.HTTPError(400, u'Unexpected error while deleting notebook: %s' % e)
        else:
            self.delete_notebook_id(notebook_id)


    def get_checkpoint_path(self, notebook_id, checkpoint_id):
        '''
        Returns the canonical checkpoint path based on the notebook_id and
        checkpoint_id
        '''
        checkpoint_path = "{}/checkpoints/{}".format(notebook_id, checkpoint_id)
        return checkpoint_path

    # Required Checkpoint methods

    def create_checkpoint(self, notebook_id):
        '''
        Create a checkpoint of the current state of a notebook

        Returns a checkpoint_id for the new checkpoint.
        '''

        self.log.debug("Creating checkpoint for notebook {}".format(
                        notebook_id))

        # We pull the next available checkpoint #
        checkpoint_id = unicode(self.next_checkpoint.setdefault(notebook_id,0))

        checkpoint_path = self.get_checkpoint_path(notebook_id, checkpoint_id)

        last_modified = utcnow()

        metadata = {
            METADATA_CHK_ID: checkpoint_id,
            METADATA_LAST_MODIFIED: last_modified.strftime(DATE_FORMAT),
            METADATA_NB_ID: notebook_id
        }
        print("Storing metadataaaaaa: {}".format(metadata))

        try:
            print("copy notebook: {} -> {}".format(notebook_id, checkpoint_path))
            self.cf.copy_object(container=self.container_name,
                       obj_name=notebook_id,
                       new_container=self.container_name,
                       new_obj_name=checkpoint_path)

            obj = self.container.get_object(checkpoint_path)
            print("obj: {}".format(obj))
            print("metadata: {}".format(metadata))
            obj.set_metadata(metadata)
            print("Metadata set".format(obj))

        except Exception as e:
            raise web.HTTPError(400, u'Unexpected error while saving checkpoint: {}'.format(e))


        info = dict(
                checkpoint_id = checkpoint_id,
                last_modified = last_modified,
        )

        self.next_checkpoint[notebook_id] = self.next_checkpoint[notebook_id] + 1

        return info

    def list_checkpoints(self, notebook_id):
        '''
        Return a list of checkpoints for a given notebook
        '''
        # Going to have to re-think this later. This is just something to try
        # out for the moment
        self.log.debug("Listing checkpoints for notebook {}".format(
                        notebook_id))
        try:
            objects = self.container.get_objects()

            chkpoints = []
            for obj in objects:
                if(notebook_id in obj.name and "checkpoints" in obj.name):
                    try:
                        print("Getting metadata")
                        metadata = obj.get_metadata()
                        print("MetaDATAAAAAA: {}".format(metadata))
                        last_modified = datetime.strptime(metadata[METADATA_LAST_MODIFIED],
                                DATE_FORMAT)
                        print(last_modified)
                        info = dict(
                            checkpoint_id = metadata[METADATA_CHK_ID],
                            last_modified = metadata[METADATA_LAST_MODIFIED],
                        )
                        chkpoints.append(info)
                        print(chkpoints)
                    except Exception as e:
                        self.log.error("Unable to pull metadata")
                        print(e)
                        pass

        except Exception as e:
            raise web.HTTPError(400, "Unexpected error while listing checkpoints")

        return chkpoints

    def restore_checkpoint(self, notebook_id, checkpoint_id):
        '''
        Restore a notebook from one of its checkpoints.

        Actually overwrites the existing notebook
        '''

        self.log.debug("Restoring checkpoint {} for notebook {}".format(
                        checkpoint_id, notebook_id))

        if not self.notebook_exists(notebook_id):
            raise web.HTTPError(404, u'Notebook does not exist: %s' % notebook_id)

        checkpoint_path = self.get_checkpoint_path(notebook_id, checkpoint_id)

        try:
            self.cf.copy_object(container=self.container_name,
                                   obj_name=checkpoint_path,
                                   new_container=self.container_name,
                                   new_obj_name=notebook_id)
        except:
            raise web.HTTPError(500, u'Checkpoint could not be restored.')

    def delete_checkpoint(self, notebook_id, checkpoint_id):
        '''
        Delete a checkpoint for a notebook
        '''

        self.log.debug("Deleting checkpoint {} for notebook {}".format(
                        checkpoint_id, notebook_id))

        if not self.notebook_exists(notebook_id):
            raise web.HTTPError(404, u'Notebook does not exist: %s' % notebook_id)

        checkpoint_path = self.get_checkpoint_path(notebook_id, checkpoint_id)

        try:
            self.container.delete_object(checkpoint_path)
        except Exception as e:
            raise web.HTTPError(400, u'Unexpected error while deleting notebook: %s' % e)

    def info_string(self):
        info = "Serving {}'s notebooks from OpenStack Swift storage container: {}"
        return info.format(self.account_name, self.container_name)


class KeystoneNotebookManager(SwiftNotebookManager):
    '''
    Manages IPython notebooks on OpenStack Swift, using Keystone
    authentication.

    Extend this class with the defaults for your OpenStack provider to make
    configuration for clients easier.
    '''
    account_name = Unicode('', config=True, help='OpenStack account name.')
    account_key = Unicode('', config=True, help='OpenStack account key.')
    auth_endpoint = Unicode('', config=True, help='Authentication endpoint.')
    region = Unicode('RegionOne', config=True, help='Region (e.g. RegionOne, ORD, LON)')
    tenant_id = Unicode('', config=True, help='The tenant ID used for authentication')
    tenant_name = Unicode('', config=True, help='The tenant name used for authentication')
    identity_type = 'keystone'

    def __init__(self, **kwargs):
        super(SwiftNotebookManager, self).__init__(**kwargs)
        pyrax.set_setting("identity_type", self.identity_type)
        pyrax.set_setting("auth_endpoint", self.auth_endpoint)
        pyrax.set_setting("region", self.region)
        pyrax.set_setting("tenant_id", self.tenant_id)
        pyrax.set_setting("tenant_name", self.tenant_name)

        # Set creds and authenticate
        pyrax.set_credentials(username=self.account_name, api_key=self.account_key)

        self.cf = pyrax.cloudfiles

        try:
            self.container = self.cf.get_container(self.container_name)
        except NoSuchContainer:
            self.container = self.cf.create_container(self.container_name)

