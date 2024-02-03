#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from simple_lambda_container.ops import pip_install_doc

    pip_install_doc()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.pip_install_doc()