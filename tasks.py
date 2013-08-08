#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bookstore
from invoke import run, task


@task
def test():
    run('py.test', pty=True)
