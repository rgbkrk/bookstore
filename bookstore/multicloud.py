#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
A notebook manager that uses libcloud to work across providers.

Requires IPython 1.1.0+

Add this to your ipython notebook profile (`ipython_notebook_config.py`),
filling in details for your provider



It's easy to set up a notebook profile if you don't have one:

    $ ipython profile create bookstore
    [ProfileCreate] Generating default config file: '/Users/theuser/.ipython/profile_bookstore/ipython_config.py'
    [ProfileCreate] Generating default config file: '/Users/theuser/.ipython/profile_bookstore/ipython_notebook_config.py'

You can also use your default config, located at

~/.ipython/profile_default/ipython_notebook_config.py

Notebooks are stored by uuid and checkpoints are stored relative to this uuid

    {notebook_id}/checkpoints/{checkpoint_id}

"""

from datetime import datetime

import libcloud

from libcloud.storage.types import Provider, ContainerDoesNotExistError
from libcloud.storage.providers import get_driver

from tornado import web

from IPython.html.services.notebooks.nbmanager import NotebookManager

from IPython.nbformat import current
from IPython.utils.traitlets import Unicode
from IPython.utils.tz import utcnow, tzUTC

import uuid

from bookstore import __version__

METADATA_NBNAME = 'nbname'
METADATA_CHK_ID = 'checkpoint-id'
METADATA_LAST_MODIFIED = 'nb-last-modified'
METADATA_NB_ID = 'notebook-id'

DATE_FORMAT = "%X-%x"

NB_DNEXIST_ERR = 'Notebook does not exist: {}'
NB_SAVE_UNK_ERR = 'Unexpected error while saving notebook: {}'
NB_DEL_UNK_ERR = 'Unexpected error while deleting notebook: {}'
CHK_SAVE_UNK_ERR = 'Unexpected error while saving checkpoint: {}'


class LibcloudNotebookManager(NotebookManager):
    """This is a base class to be subclassed to simplify other providers.
    """

    user_agent = "bookstore v{version}".format(version=__version__)
    container_name = Unicode('notebooks', config=True,
                             help='Container name for notebooks.')

    def __init__(self, **kwargs):
        super(LibcloudNotebookManager, self).__init__(**kwargs)

        # TODO: Set custom user agent for libcloud
        # client.connection.user_agent_append(self.user_agent)

    def load_notebook_names(self):
        """On startup load the notebook ids and names from the container.

        The object names are the notebook ids and the notebook names are stored
        as object metadata.
        """
        # Cached version of the mapping of notebook IDs to notebook names
        self.mapping = {}

        # Grab only top level notebooks
        top_level = lambda obj: "/" not in obj.name 

        object_iters = ifilter(top_level, container.iterate_objects())

        for obj in object_iters
            nb_id = obj.name
            metadata = obj.meta_data

            # TODO: Check on this metadata setting (current notebooks don't
            # have it set, it seems)
            if(METADATA_NBNAME in metadata):
                name = metadata[METADATA_NBNAME]
                self.mapping[nb_id] = name

    def list_notebooks(self):
        """List all notebooks in the container.

        This version uses `self.mapping` as the authoritative notebook list.
        """
        data = [dict(notebook_id=nb_id, name=name)
                for nb_id, name in list(self.mapping.items())]
        data = sorted(data, key=lambda item: item['name'])
        return data

    def _read_notebook_object(self, notebook_path):
        try:
            obj = self.container.get_object(notebook_id)
            obj_stream = obj.as_stream()
            s = "".join(list(obj_stream))
        except:
            raise web.HTTPError(500, 'Notebook cannot be read.')

        try:
            nb = current.reads(s, 'json')
        except:
            raise web.HTTPError(500, 'Unreadable JSON notebook.')

        # TODO: Check if this really means the last_modified (only read here)
        last_modified = utcnow()
        return last_modified, nb

    def read_notebook_object(self, notebook_id):
        """Get the object representation of a notebook by notebook_id."""
        if not self.notebook_exists(notebook_id):
            raise web.HTTPError(404, NB_DNEXIST_ERR.format(notebook_id))

        return self._read_notebook_object(notebook_id)

    def write_notebook_object(self, nb, notebook_id=None):
        """Save an existing notebook object by notebook_id."""

        try:
            new_name = nb.metadata.name
        except AttributeError:
            raise web.HTTPError(400, 'Missing notebook name')

        if notebook_id is None:
            notebook_id = self.new_notebook_id(new_name)

        if notebook_id not in self.mapping:
            raise web.HTTPError(404, NB_DNEXIST_ERR.format(notebook_id))

        try:
            data = current.writes(nb, 'json')
        except Exception as e:
            raise web.HTTPError(400, NB_SAVE_UNK_ERR.format(e))

        metadata = {METADATA_NBNAME: new_name}
        try:
            obj = self.container.store_object(iterator=iter(data),
                                              object_name=notebook_id,
                                              extra={'content_type':'application/json',
                                                     'meta_data': metadata})
        except Exception as e:
            raise web.HTTPError(400, NB_SAVE_UNK_ERR.format(e))

        self.mapping[notebook_id] = new_name
        return notebook_id

    def delete_notebook(self, notebook_id):
        """Delete notebook by notebook_id.

        Also deletes checkpoints for the notebook.
        """
        if not self.notebook_exists(notebook_id):
            raise web.HTTPError(404, NB_DNEXIST_ERR.format(notebook_id))
        try:
            deletable_notebooks = lambda obj: obj.startswith(notebook_id)

            object_iters = ifilter(deletable_notebooks,
                                   container.iterate_objects())

            for obj in object_iters:
                obj.delete()

        except Exception as e:
            raise web.HTTPError(400, NB_DEL_UNK_ERR.format(e))
        else:
            self.delete_notebook_id(notebook_id)

    def get_checkpoint_path(self, notebook_id, checkpoint_id):
        """Returns the canonical checkpoint path based on the notebook_id and
        checkpoint_id
        """
        checkpoint_path_format = "{}/checkpoints/{}"
        return checkpoint_path_format.format(notebook_id, checkpoint_id)

    def new_checkpoint_id(self):
        """Generate a new checkpoint_id and store its mapping."""
        return unicode(uuid.uuid4())

    # Required Checkpoint methods

    def _copy_notebook(self, notebook_path, new_notebook_path, checkpoint_id):
        try:
            self.log.info("Copying notebook {} to {}".format(
                notebook_id, checkpoint_path))

            last_modified, nb = self._read_notebook_object(notebook_id)

            metadata = {
                METADATA_CHK_ID: checkpoint_id,
                METADATA_LAST_MODIFIED: last_modified.strftime(DATE_FORMAT),
                METADATA_NB_ID: notebook_id
            }

            obj = self.container.store_object(iterator=iter(data),
                                              object_name=checkpoint_path,
                                              extra={'content_type':'application/json',
                                                     'meta_data': metadata})    
        except Exception as e:
            raise web.HTTPError(400, CHK_SAVE_UNK_ERR.format(e))

        return obj, last_modified

    def create_checkpoint(self, notebook_id):
        """Create a checkpoint of the current state of a notebook

        Returns a dictionary with a checkpoint_id and the timestamp from the
        last modification

        Subclasses of providers that provide a copy object semantic should
        override this class.
        """

        self.log.info("Creating checkpoint for notebook {}".format(
                      notebook_id))

        checkpoint_id = self.new_checkpoint_id()

        checkpoint_path = self.get_checkpoint_path(notebook_id, checkpoint_id)

        self._copy_notebook(notebook_id, checkpoint_path, checkpoint_id)

        except Exception as e:
            raise web.HTTPError(400, CHK_SAVE_UNK_ERR.format(e))

        info = dict(checkpoint_id=checkpoint_id,
                    last_modified=last_modified)

        return info

    def list_checkpoints(self, notebook_id):
        """Return a list of checkpoints for a given notebook"""
        # Grab only checkpoints for this notebook
        my_checkpoints = lambda obj: obj.startswith(notebook_id + "/")

        object_iters = ifilter(my_checkpoints, container.iterate_objects())
        self.log.info("Listing checkpoints for notebook {}".format(
                      notebook_id))


        try:
            checkpoints = []

            for obj in object_iters:
                metadata = obj.meta_data
                self.log.debug("Object: {}".format(obj.name))
                self.log.debug("Metadata: {}".format(metadata))

                last_modified = datetime.strptime(
                    metadata[METADATA_LAST_MODIFIED],
                    DATE_FORMAT)

                last_modified = last_modified.replace(tzinfo=tzUTC())
                info = dict(
                    checkpoint_id=metadata[METADATA_CHK_ID],
                    last_modified=last_modified,
                )
                checkpoints.append(info)

        except Exception as e:
            raise web.HTTPError(400, "Unexpected error while listing" +
                                     "checkpoints")

        checkpoints = sorted(checkpoints, key=lambda item: item['last_modified'])

        self.log.debug("Checkpoints to list: {}".format(checkpoints))

        return checkpoints

    def restore_checkpoint(self, notebook_id, checkpoint_id):
        """Restore a notebook from one of its checkpoints.

        Actually overwrites the existing notebook
        """

        self.log.info("Restoring checkpoint {} for notebook {}".format(
                      checkpoint_id, notebook_id))

        if not self.notebook_exists(notebook_id):
            raise web.HTTPError(404, NB_DNEXIST_ERR.format(notebook_id))

        checkpoint_path = self.get_checkpoint_path(notebook_id, checkpoint_id)

        try:
            self.cf.copy_object(container=self.container_name,
                                obj=checkpoint_path,
                                new_container=self.container_name,
                                new_obj_name=notebook_id)
        except:
            raise web.HTTPError(500, 'Checkpoint could not be restored.')

    def delete_checkpoint(self, notebook_id, checkpoint_id):
        """Delete a checkpoint for a notebook"""

        self.log.info("Deleting checkpoint {} for notebook {}".format(
                      checkpoint_id, notebook_id))

        if not self.notebook_exists(notebook_id):
            raise web.HTTPError(404, NB_DNEXIST_ERR.format(notebook_id))

        checkpoint_path = self.get_checkpoint_path(notebook_id, checkpoint_id)

        try:
            self.container.delete_object(checkpoint_path)
        except Exception as e:
            nb_delete_err_msg = 'Unexpected error while deleting notebook: {}'
            raise web.HTTPError(400, nb_delete_err_msg.format(e))

    def info_string(self):
        info = ("Serving {}'s notebooks from OpenStack Swift "
                "storage container: {}")
        return info.format(self.account_name, self.container_name)


class KeystoneNotebookManager(SwiftNotebookManager):
    """Manages IPython notebooks on OpenStack Swift, using Keystone
    authentication.

    Extend this class with the defaults for your OpenStack provider to make
    configuration for clients easier.
    """
    account_name = Unicode('', config=True, help='OpenStack account name.')
    account_key = Unicode('', config=True, help='OpenStack account key.')
    auth_endpoint = Unicode('', config=True, help='Authentication endpoint.')

    region = Unicode('RegionOne', config=True,
                     help='Region (e.g. RegionOne, ORD, LON)')

    tenant_id = Unicode('', config=True,
                        help='The tenant ID used for authentication')
    tenant_name = Unicode('', config=True,
                          help='The tenant name used for authentication')

    identity_type = 'keystone'

    def __init__(self, **kwargs):
        super(SwiftNotebookManager, self).__init__(**kwargs)
        pyrax.set_setting("identity_type", self.identity_type)
        pyrax.set_setting("auth_endpoint", self.auth_endpoint)
        pyrax.set_setting("region", self.region)
        pyrax.set_setting("tenant_id", self.tenant_id)
        pyrax.set_setting("tenant_name", self.tenant_name)

        # Set creds and authenticate
        pyrax.set_credentials(username=self.account_name,
                              api_key=self.account_key)

        self.cf = pyrax.cloudfiles

        try:
            self.container = self.cf.get_container(self.container_name)
        except NoSuchContainer:
            self.container = self.cf.create_container(self.container_name)
