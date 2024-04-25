#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from aws_idp_doc.ops import poetry_export

    poetry_export()
except ImportError:
    from automation.api import pyproject_ops

    pyproject_ops.poetry_export()
