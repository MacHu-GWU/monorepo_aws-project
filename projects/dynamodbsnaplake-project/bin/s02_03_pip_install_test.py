#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from dynamodbsnaplake.ops import pip_install_test

    pip_install_test()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.pip_install_test()
