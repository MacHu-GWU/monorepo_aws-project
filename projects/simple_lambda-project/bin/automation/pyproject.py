# -*- coding: utf-8 -*-

"""
Parse the ``pyproject.toml`` file.
"""

from pyproject_ops.api import PyProjectOps

from .paths import path_pyproject_toml

pyproject_ops = PyProjectOps.from_pyproject_toml(path_pyproject_toml)
