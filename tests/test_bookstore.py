#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""
Tests for bookstore
"""

import logging
import unittest
import doctest

import swiftclient
from bookstore import SwiftNotebookManager
from IPython.html.services.notebooks.tests.test_nbmanager import TestNotebookManager

logging.getLogger('swiftclient').setLevel(logging.CRITICAL)
logging.getLogger('keystoneclient').setLevel(logging.WARN)
logging.getLogger('iso8601').setLevel(logging.WARN)
logging.getLogger('requests').setLevel(logging.WARN)
logging.basicConfig(level=logging.DEBUG)

class TestSwiftNotebookManager(TestNotebookManager):
    container = "test_container"

    def setUp(self):
        self.notebook_manager = SwiftNotebookManager(
            log=logging.getLogger(),
            container=self.container
        )
        # TestNotebookManager expects NotebookManager to have
        # notebook_dir
        self.notebook_manager.notebook_dir = 'foo'

    def tearDown(self):
        try:    
            _, objs = self.notebook_manager.connection.get_container(self.container)
            for o in objs:
                self.notebook_manager.connection.delete_object(self.container, o['name'])
        except swiftclient.ClientException as e:
            print("exception during tearDown %s" % e)
            print("container was %s " % objs)
            print("couldn't delete object %s " % o['name'])

    # we do not support saving the script
    def test_save_notebook_with_script(self):
        pass

if __name__ == "__main__":
    unittest.main()
