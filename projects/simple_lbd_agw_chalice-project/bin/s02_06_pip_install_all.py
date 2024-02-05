#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from simple_lbd_agw_chalice.ops import pip_install_all

    pip_install_all()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.pip_install_all()
