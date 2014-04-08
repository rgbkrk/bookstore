#!/usr/bin/env python

# -*- coding: utf-8 -*-

from datetime import datetime
import dateutil.parser

import os.path
from six import BytesIO

import swiftclient

from tornado import web

from IPython.html.services.notebooks.nbmanager import NotebookManager

from IPython.nbformat import current
from IPython.utils.traitlets import Unicode
from IPython.utils.tz import utcnow, tzUTC

import uuid

from bookstore import __version__

class SwiftNotebookManager(NotebookManager):
    """This is a base class to be subclassed by OpenStack providers. The swift
    object storage should work across implementations, only authentication
    should differ.
    """

    container = Unicode('notebooks', config=True,
                        help='Container name for notebooks.')

    notebook_dir = Unicode(u"", config=True)

    def __init__(self, **kwargs):
        super(SwiftNotebookManager, self).__init__(**kwargs)

    def path_exists(self, path):
        self.log.info("list_dirs('{}')".format(path))
        return True

    def is_hidden(self, path):
        self.log.info("is_hidden('{}')".format(path))
        return False

    def notebook_exists(self, name, path=''):
        """Returns a True if the notebook exists. Else, returns False."""
        self.log.info("notebook_exists('{}','{}')".format(name, path))

        full_path = os.path.join(path, name)
        try:
            hdrs = self.connection.head_object(self.container, full_path)
            return True
        except:
            return False

    # The method list_dirs is called by the server to identify
    # the subdirectories in a given path.
    def list_dirs(self, path):
        """List the directory models for a given API style path."""
        self.log.info("list_dirs('{}')".format(path))
        return []

    def list_notebooks(self, path=''):
        """Return a list of notebook dicts without content."""
        self.log.info("list_notebooks('{}')".format(path))

        if path != '' and not path.endswith('/'):
            path = path + '/'
        _, conts = self.connection.get_container(
            self.container, prefix=path, delimiter='/')

        notebooks = [{
            'name': os.path.basename(obj['name']),
            'path': obj['name'],
            'last_modified': dateutil.parser.parse(obj['last_modified']),
            'created': dateutil.parser.parse(obj['last_modified']),
            'type': 'notebook'}
            for obj in conts if 'name' in obj]

        notebooks = sorted(notebooks, key=lambda item: item['name'])
        return notebooks

    def get_notebook(self, name, path='', content=True):
        """Get the notebook model with or without content."""
        self.log.info(
            "get_notebook('{}','{}','{}')".format(name, path, content))

        full_path = os.path.join(path, name)
        if content:
            hdrs, conts = self.connection.get_object(self.container, full_path)
            model = {
                'name': name,
                'path': path,
                'last_modified': dateutil.parser.parse(hdrs['last-modified']),
                'created': dateutil.parser.parse(hdrs['last-modified']),
                'type': 'notebook',
                'content': current.reads(conts, 'json')
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

    def save_notebook(self, model, name='', path=''):
        """Save the notebook model and return the model with no content."""
        self.log.info(
            "save_notebook('{}','{}','{}')".format(model, name, path))

        path = path.strip('/')

        if 'content' not in model:
            raise web.HTTPError(400, u'No notebook JSON data provided')

        # One checkpoint should always exist
        if self.notebook_exists(name, path) and not self.list_checkpoints(name, path):
            self.create_checkpoint(name, path)

        new_path = model.get('path', path).strip('/')
        new_name = model.get('name', name)
        full_path = os.path.join(new_path, new_name)

        if path != new_path or name != new_name:
            self.rename_notebook(name, path, new_name, new_path)

        nb = current.to_notebook_json(model['content'])
        self.check_and_sign(nb, new_name, new_path)
        if 'name' in nb['metadata']:
            nb['metadata']['name'] = u''

        ipynb_stream = BytesIO()
        current.write(nb, ipynb_stream, u'json')
        self.connection.put_object(
            self.container, full_path, ipynb_stream.getvalue(), content_type='application/json')
        ipynb_stream.close()

        # Return model
        model = self.get_notebook(new_name, new_path, content=False)
        return model

    def update_notebook(self, model, name, path=''):
        """Update the notebook's path and/or name"""
        self.log.info(
            "update_notebook('{}','{}','{}')".format(model, name, path))

        path = path.strip('/')
        new_name = model.get('name', name)
        new_path = model.get('path', path).strip('/')
        if path != new_path or name != new_name:
            self._rename_notebook(name, path, new_name, new_path)
        model = self.get_notebook(new_name, new_path, content=False)
        return model

    def delete_notebook(self, name, path=''):
        """Delete notebook by name and path."""
        self.log.info("delete_notebook('{}','{}')".format(name, path))

        full_path = os.path.join(path, name)
        hdrs, conts = self.connection.get_container(
            self.container, prefix=full_path + '/', delimiter='/')
        for obj in conts:
            self.connection.delete_object(self.container, obj['name'])
        self.connection.delete_object(self.container, full_path)

    def _rename_notebook(self, old_name, old_path, new_name, new_path):
        """Rename a notebook."""
        self.log.info("_rename_notebook('{}','{}','{}','{}')".format(
            old_name, old_path, new_name, new_path))

        old_path = old_path.strip('/')
        new_path = new_path.strip('/')
        if new_name == old_name and new_path == old_path:
            return

        new_path = os.path.join(new_path, new_name)
        old_path = os.path.join(old_path, old_name)

        # Should we proceed with the move?
        if self.notebook_exists(new_name, new_path):
            raise web.HTTPError(
                409, u'Notebook with name already exists: %s' % new_path)
        self.log.info("TODO in rename_notebook() I am ignoring save_script")

        # Move the checkpoints
        hdrs, conts = self.connection.get_container(
            self.container, prefix=old_path + '/', delimiter='/')
        for obj in conts:
            old_checkpoint_path = obj['name']
            new_checkpoint_path = old_checkpoint_path.replace(
                old_path, new_path)
            self.connection.put_object(self.container, new_checkpoint_path,
                                       contents=None,
                                       headers={'X-Copy-From': '/%s/%s' % (self.container, old_checkpoint_path)})
            self.connection.delete_object(self.container, old_checkpoint_path)

        # Move the notebook file
        self.connection.put_object(self.container, new_path,
                                   contents=None,
                                   headers={'X-Copy-From': '/%s/%s' % (self.container, old_path)})
        self.connection.delete_object(self.container, old_path)

    def create_checkpoint(self, name, path=''):
        """Create a checkpoint of the current state of a notebook"""
        self.log.info("create_checkpoint('{}','{}')".format(name, path))

        checkpoint_id = unicode(uuid.uuid4())

        full_path = os.path.join(path, name)
        checkpoint_path = os.path.join(path, name, checkpoint_id)

        self.connection.put_object(self.container, checkpoint_path,
                                   contents=None,
                                   headers={'X-Copy-From': '/%s/%s' % (self.container, full_path)})

        last_modified = utcnow()
        return {'id': checkpoint_id, 'last_modified': last_modified}

    def list_checkpoints(self, name, path=''):
        """Return a list of checkpoints for a given notebook"""
        self.log.info("list_checkpoints('{}','{}')".format(name, path))

        full_path = os.path.join(path, name)
        hdrs, data = self.connection.get_container(self.container,
                                                   prefix=full_path + '/', delimiter='/')

        checkpoints = [{
            'id': os.path.basename(obj['name']),
            'last_modified': dateutil.parser.parse(obj['last_modified'])
        } for obj in data]

        checkpoints = sorted(
            checkpoints, key=lambda item: item['last_modified'])
        self.log.info("Checkpoints to list: {}".format(checkpoints))
        return checkpoints

    def restore_checkpoint(self, checkpoint_id, name, path=''):
        """Restore a notebook from one of its checkpoints"""
        self.log.info(
            "restore_checkpoint('{}','{}','{}')".format(checkpoint_id, name, path))

        assert name.endswith(self.filename_ext)
        assert self.notebook_exists(name, path)

        full_path = os.path.join(path, name)
        checkpoint_path = os.path.join(path, name, checkpoint_id)

        self.connection.put_object(self.container, full_path,
                                   contents=None,
                                   headers={'X-Copy-From': '/%s/%s' % (self.container, checkpoint_path)})

    def delete_checkpoint(self, notebook_id, checkpoint_id):
        """Delete a checkpoint for a notebook"""
        self.log.info(
            "delete_checkpoint('{}','{}')".format(notebook_id, checkpoint_id))

        checkpoint_path = os.path.join(path, name, checkpoint_id)
        self.connection.delete_object(self.container, checkpoint_path)

    def info_string(self):
        info = ("Serving {}'s notebooks from OpenStack Swift "
                "storage container: {}")
        return info.format(self.account_name, self.container)

