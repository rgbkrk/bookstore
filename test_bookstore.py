#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for hexview
"""

import unittest
import doctest

import bookstore

class HexviewTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_entry_points(self):
        bookstore.swift
        bookstore.cloudfiles

if __name__ == "__main__":
    unittest.main()
