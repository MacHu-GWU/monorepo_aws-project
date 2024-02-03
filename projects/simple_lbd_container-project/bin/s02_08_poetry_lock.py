#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from simple_lbd_container.ops import poetry_lock

    poetry_lock()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.poetry_lock()
