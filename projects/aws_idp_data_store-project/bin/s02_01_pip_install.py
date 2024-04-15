#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from aws_idp_data_store.ops import pip_install

    pip_install()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.pip_install()
