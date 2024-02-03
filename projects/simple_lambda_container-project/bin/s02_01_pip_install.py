#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from simple_lambda_container.ops import pip_install

    pip_install()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.pip_install()