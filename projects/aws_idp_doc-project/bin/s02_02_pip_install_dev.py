#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from aws_idp_doc.ops import pip_install_dev

    pip_install_dev()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.pip_install_dev()
