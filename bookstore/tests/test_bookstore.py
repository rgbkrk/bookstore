"""Tests for bookstore"""
from __future__ import print_function

import logging
import unittest
import os

from bookstore import SwiftNotebookManager
from .test_nbmanager import TestNotebookManager


class TestSwiftNotebookManager(TestNotebookManager, unittest.TestCase):

    """
    This class tests SwiftNotebookManager. It uses TestNotebookManager mix-in.
    """

    container = "test_container"
    connection_args = {
        'authurl': os.environ['OS_AUTH_URL'],
        'user': os.environ['OS_USERNAME'],
        'key': os.environ['OS_PASSWORD'],
        'auth_version': os.environ['OS_AUTH_VERSION'],
        'os_options': {
            'tenant_id': os.environ['OS_TENANT_ID'],
            'tenant_name': os.environ['OS_TENANT_NAME']
        }
    }

    @classmethod
    def setUpClass(cls):
        cls.notebook_manager = SwiftNotebookManager(
            log=logging.getLogger(),
            container=cls.container,
            connection_args=cls.connection_args)

    @classmethod
    def tearDownClass(cls):
        cls.notebook_manager.connection.delete_container(cls.container)

    def tearDown(self):
        _, objs = self.notebook_manager.connection.get_container(
            self.container)
        for o in objs:
            self.notebook_manager.connection.delete_object(
                self.container, o['name'])
