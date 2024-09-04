#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from simple_deploy_gate.ops import pip_install_dev

    pip_install_dev()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.pip_install_dev()
