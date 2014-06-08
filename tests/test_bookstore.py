#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for bookstore
"""

import unittest
import doctest

import bookstore


class BookstoreTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_entry_points(self):
        bookstore.swift

if __name__ == "__main__":
    unittest.main()
