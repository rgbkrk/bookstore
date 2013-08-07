#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hexview

from invoke import run, task

@task
def test():
    run('py.test', pty=True)
