#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from aws_idp_data_store.ops import poetry_lock

    poetry_lock()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.poetry_lock()
