#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from simple_deploy_gate.ops import poetry_export

    poetry_export()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.poetry_export()
