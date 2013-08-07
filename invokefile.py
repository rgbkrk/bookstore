#!/usr/bin/env python
# -*- coding: utf-8 -*-

from invoke import run, task

@task
def build():
    print("Building!")
