#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from simple_deploy_gate.ops import pip_install_automation

    pip_install_automation()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.pip_install_automation()
