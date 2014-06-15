#!/usr/bin/env python

# -*- coding: utf-8 -*-

import dateutil.parser
import os
import posixpath
from six import BytesIO

from tornado.web import HTTPError

from IPython.html.services.notebooks.nbmanager import NotebookManager
from IPython.nbformat import current
from IPython.utils.traitlets import Unicode, TraitError
from IPython.utils.tz import utcnow

import uuid
from swiftclient import Connection, ClientException


class SwiftNotebookManager(NotebookManager):

    """A notebook manager that uses OpenStack Swift object storage, using Keystone
    authentication

    Requires IPython 2.0+

    Add this to your ipython notebook profile (`ipython_notebook_config.py`),
    filling in details for your OpenStack implementation.

        # Setup IPython Notebook to write notebooks to a OpenSwift storage
        c.NotebookApp.notebook_manager_class = 'bookstore.SwiftNotebookManager'

        # Set your user name and API Key
        c.SwiftNotebookManager.auth_url = OS_AUTH_URL
        c.SwiftNotebookManager.user_name = OS_USERNAME
        c.SwiftNotebookManager.password = OS_PASSWORD
        c.SwiftNotebookManager.tenant_name = OS_TENANT_NAME

        # Name of the container on OpenStack Swift
        c.SwiftNotebookManager.container_name = u'notebooks'
    """

    def path_exists(self, path):
        self.log.debug(u"path_exists('{}')".format(path))
        return True

    def is_hidden(self, path):
        self.log.debug(u"is_hidden('{}')".format(path))
        return False

    def _copy_object(self, old_path, new_path):
        old_path = old_path.strip('/')
        new_path = new_path.strip('/')
        headers = {
            u'X-Copy-From': posixpath.join(self.container, old_path)
        }
        self.connection.put_object(self.container, new_path,
                                   contents=None, headers=headers)

    def _move_object(self, old_path, new_path):
        old_path = old_path.strip('/')
        new_path = new_path.strip('/')
        self._copy_object(old_path, new_path)

        hdrs, conts = self.connection.get_object(self.container, old_path)
        self.log.debug("before delete_object: {}".format(old_path))
        self.log.debug("before delete_object:\nhdrs = {}\nconts = {}".format(hdrs, conts))
        self.connection.delete_object(self.container, old_path)


    def notebook_exists(self, name, path=''):
        """Returns a True if the notebook exists. Else, returns False."""
        path = path.strip('/')

        self.log.debug(u"notebook_exists('{}','{}')".format(name, path))

        full_path = posixpath.join(path, name)
        try:
            self.connection.head_object(self.container, full_path)
            return True
        except ClientException as e:
            if e.http_status == 404:
                return False
            else:
                raise

    # The method list_dirs is called by the server to identify
    # the subdirectories in a given path.
    def list_dirs(self, path):
        """List the directory models for a given API style path."""
        self.log.debug(u"list_dirs('{}')".format(path))
        return []

    def list_notebooks(self, path=''):
        """Return a list of notebook dicts without content."""
        path = path.strip('/')

        self.log.debug(u"list_notebooks('{}')".format(path))

        _, conts = self.connection.get_container(
            self.container, prefix=path + '/', delimiter='/')

        notebooks = [{
            'name': posixpath.basename(obj['name']),
            'path': obj['name'],
            'last_modified': dateutil.parser.parse(obj['last_modified']),
            'created': dateutil.parser.parse(obj['last_modified']),
            'type': 'notebook'}
            for obj in conts if 'name' in obj]

        notebooks = sorted(notebooks, key=lambda item: item['name'])
        return notebooks

    def get_notebook(self, name, path='', content=True):
        """Get the notebook model with or without content."""
        path = path.strip('/')

        self.log.debug(
            u"get_notebook('{}','{}','{}')".format(name, path, content))

        try:
            full_path = posixpath.join(path, name)
            if content:
                hdrs, conts = self.connection.get_object(self.container, full_path)
                nb = current.reads(conts, 'json')
                self.mark_trusted_cells(nb, path, name)
                model = {
                    'name': name,
                    'path': path,
                    'last_modified': dateutil.parser.parse(hdrs['last-modified']),
                    'created': dateutil.parser.parse(hdrs['last-modified']),
                    'type': 'notebook',
                    'content': nb
                }
                return model
            else:
                hdrs = self.connection.head_object(self.container, full_path)
                model = {
                    'name': name,
                    'path': path,
                    'last_modified': dateutil.parser.parse(hdrs['last-modified']),
                    'created': dateutil.parser.parse(hdrs['last-modified']),
                    'type': 'notebook',
                }
                return model
        except ClientException as e:
            if e.http_status == 404:
                raise HTTPError(
                    404, u'Notebook not found: %s' % full_path)
            else:
                raise

    def save_notebook(self, model, name='', path=''):
        """Save the notebook model and return the model with no content."""
        path = path.strip('/')

        self.log.debug(
            u"save_notebook('{}','{}','{}')".format(model, name, path))

        if 'content' not in model:
            raise HTTPError(400, u'No notebook JSON data provided')

        # # One checkpoint should always exist
        # if (self.notebook_exists(name, path) and
        #         not self.list_checkpoints(name, path)):
        #     self.create_checkpoint(name, path)

        new_name = model.get('name', name)
        new_path = model.get('path', path).strip('/')
        full_path = posixpath.join(new_path, new_name)

        if path != new_path or name != new_name:
            self.rename_notebook(name, path, new_name, new_path)

        nb = current.to_notebook_json(model['content'])
        self.check_and_sign(nb, new_name, new_path)
        if 'name' in nb['metadata']:
            nb['metadata']['name'] = u''

        ipynb_stream = BytesIO()
        current.write(nb, ipynb_stream, u'json')
        data = ipynb_stream.getvalue()
        self.connection.put_object(self.container, full_path, data,
                                   content_type='application/json')
        ipynb_stream.close()

        # Return model
        model = self.get_notebook(new_name, new_path, content=False)
        return model

    def update_notebook(self, model, name, path=''):
        """Update the notebook's path and/or name"""
        path = path.strip('/')

        self.log.debug(
            u"update_notebook('{}','{}','{}')".format(model, name, path))

        new_name = model.get('name', name)
        new_path = model.get('path', path).strip('/')
        if path != new_path or name != new_name:
            self.log.debug("renaming {}/{} to {}/{}".format(path, name, new_path, new_name))
            _, data = \
                self.connection.get_container(self.container)
            self.log.debug("pre container = {}".format(data))
            self._rename_notebook(name, path, new_name, new_path)
            _, data = \
                self.connection.get_container(self.container)
            self.log.debug("post container = {}".format(data))
        model = self.get_notebook(new_name, new_path, content=False)
        return model

    def delete_notebook(self, name, path=''):
        """Delete notebook by name and path."""
        path = path.strip('/')

        self.log.debug(u"delete_notebook('{}','{}')".format(name, path))

        checkpoints = self.list_checkpoints(name, path)
        for checkpoint in checkpoints:
            self.delete_checkpoint(checkpoint['id'], name, path)

        try:
            full_path = posixpath.join(path, name)
            self.connection.delete_object(self.container, full_path)
        except ClientException as e:
            if e.http_status == 404:
                raise HTTPError(
                    404, u'Notebook not found: %s' % full_path)
            else:
                raise

    def _rename_notebook(self, old_name, old_path, new_name, new_path):
        """Rename a notebook."""
        old_path = old_path.strip('/')
        new_path = new_path.strip('/')

        self.log.debug(u"_rename_notebook('{}','{}','{}','{}')".format(
            old_name, old_path, new_name, new_path))

        if new_name == old_name and new_path == old_path:
            return

        # Should we proceed with the move?
        if self.notebook_exists(new_name, new_path):
            raise HTTPError(
                409, u'Notebook with name already exists: %s' % new_path)

        # Move the checkpoints
        checkpoints = self.list_checkpoints(old_name, old_path)
        for checkpoint in checkpoints:
            old_checkpoint_path = self._checkpoint_path(checkpoint['id'], old_name, old_path)
            new_checkpoint_path = self._checkpoint_path(checkpoint['id'], new_name, new_path)
            self._move_object(old_checkpoint_path, new_checkpoint_path)

        new_full_path = posixpath.join(new_path, new_name)
        old_full_path = posixpath.join(old_path, old_name)

        self._move_object(old_full_path, new_full_path)

    def _checkpoint_path(self, checkpoint_id, name, path):
        return posixpath.join(path, name, checkpoint_id)

    def create_checkpoint(self, name, path=''):
        """Create a checkpoint of the current state of a notebook"""
        path = path.strip('/')

        self.log.debug(u"create_checkpoint('{}','{}')".format(name, path))

        checkpoint_id = unicode(uuid.uuid4())

        full_path = posixpath.join(path, name)
        checkpoint_path = self._checkpoint_path(checkpoint_id, name, path)
        self._copy_object(full_path, checkpoint_path)

        last_modified = utcnow()
        return {'id': checkpoint_id, 'last_modified': last_modified }

    def list_checkpoints(self, name, path=''):
        """Return a list of checkpoints for a given notebook"""
        path = path.strip('/')

        self.log.debug(u"list_checkpoints('{}','{}')".format(name, path))

        full_path = posixpath.join(path, name)
        _, data = \
            self.connection.get_container(self.container,
                                          prefix=full_path + '/',
                                          delimiter='/')

        self.log.debug(u"prefix={}".format(full_path + '/'))
        self.log.debug(u"{}".format(data))

        checkpoints = [{
            'id': posixpath.basename(obj['name']),
            'last_modified': dateutil.parser.parse(obj['last_modified'])
        } for obj in data]

        checkpoints = sorted(
            checkpoints, key=lambda item: item['last_modified'])
        self.log.debug(u"Checkpoints to list: {}".format(checkpoints))
        return checkpoints

    def restore_checkpoint(self, checkpoint_id, name, path=''):
        """Restore a notebook from one of its checkpoints"""
        path = path.strip('/')

        self.log.debug(u"restore_checkpoint('{}','{}','{}')"
                       .format(checkpoint_id, name, path))

        assert name.endswith(self.filename_ext)
        assert self.notebook_exists(name, path)

        full_path = posixpath.join(path, name)
        checkpoint_path = self._checkpoint_path(checkpoint_id, name, path)
        self._copy_object(checkpoint_path, full_path)

    def delete_checkpoint(self, checkpoint_id, name, path=''):
        """Delete a checkpoint for a notebook"""
        path = path.strip('/')

        self.log.debug(u"delete_checkpoint('{}','{}','{}')"
                       .format(checkpoint_id, name, path))

        try:
            checkpoint_path = self._checkpoint_path(checkpoint_id, name, path)
            self.connection.delete_object(self.container, checkpoint_path)
        except ClientException as e:
            if e.http_status == 404:
                raise HTTPError(
                    404, u'Checkpoint not found: %s' % checkpoint_path)
            else:
                raise

    def info_string(self):
        info = (u"Serving {}'s notebooks from OpenStack Swift "
                "storage container: {}")
        return info.format(self.user_name, self.container)

    user_name = Unicode(os.getenv('OS_USERNAME', ''), config=True,
                        help='OpenStack username. Defaults to env[OS_USERNAME].')

    password = Unicode(os.getenv('OS_PASSWORD', ''), config=True,
                       help='OpenStack password. Defaults to env[OS_PASSWORD].')

    auth_version = Unicode('2.0', config=True,
                           help='Authentication protocol version')

    tenant_id = Unicode(os.getenv('OS_TENANT_ID', ''), config=True,
                        help='OpenStack tenant ID. Defaults to env[OS_TENANT_ID].')

    tenant_name = Unicode(os.getenv('OS_TENANT_NAME', ''), config=True,
                          help='OpenStack tenant name. Defaults to env[OS_TENANT_NAME].')

    auth_url = Unicode(os.getenv('OS_AUTH_URL', ''), config=True,
                       help='OpenStack auth URL. Defaults to env[OS_AUTH_URL].')

    auth_token = Unicode(os.getenv('OS_AUTH_TOKEN', ''), config=True,
                         help='OpenStack token. Defaults to env[OS_AUTH_TOKEN]. Used with storage_url to bypass the usual username/password authentication.')

    storage_url = Unicode(os.getenv('OS_STORAGE_URL', ''), config=True,
                          help='OpenStack storage URL. Defaults to env[OS_STORAGE_URL]. Overrides the storage url returned during auth. Will bypass authentication when used with auth_token.')

    service_type = Unicode(os.getenv('OS_SERVICE_TYPE', ''), config=True,
                           help='OpenStack Service type. Defaults to env[OS_SERVICE_TYPE].')

    region_name = Unicode(os.getenv('OS_REGION_NAME', ''), config=True,
                          help='OpenStack region name. Defaults to env[OS_REGION_NAME].')

    service_type = Unicode(os.getenv('OS_SERVICE_TYPE', ''), config=True,
                           help='OpenStack Service type. Defaults to env[OS_SERVICE_TYPE].')

    endpoint_type = Unicode(os.getenv('OS_ENDPOINT_TYPE', ''), config=True,
                            help='OpenStack Endpoint type. Defaults to env[OS_ENDPOINT_TYPE].')

    cacert = Unicode(os.getenv('OS_CACERT', ''), config=True,
                     help='Specify a CA bundle file to use in verifying a TLS (https) server certificate. Defaults to env[OS_CACERT].')

    container = Unicode('notebooks', config=True,
                        help='Container name for notebooks.')

    def __init__(self, **kwargs):
        super(SwiftNotebookManager, self).__init__(**kwargs)

        try:
            os_options = {
                'auth_token': self.auth_token,
                'tenant_id': self.tenant_id,
                'tenant_name': self.tenant_name,
                'service_type': self.service_type,
                'endpoint_type': self.endpoint_type,
                'storage_url': self.storage_url,
                'region_name': self.region_name
            }
            args = {
                'authurl': self.auth_url,
                'user': self.user_name,
                'key': self.password,
                'os_options': os_options,
                'auth_version': self.auth_version,
                'cacert': self.cacert
            }
            self.connection = Connection(**args)
            self.connection.put_container(self.container)
        except ClientException as e:
            raise TraitError("Couldn't connect to notebook storage: " + str(e))
