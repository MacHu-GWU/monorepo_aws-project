# -*- coding: utf-8 -*-

"""
Parse the ``pyproject.toml`` file.
"""

import sys

from pyproject_ops.api import PyProjectOps

from .paths import dir_project_root, PACKAGE_NAME

pyproject_ops = PyProjectOps(
    python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
    package_name=PACKAGE_NAME,
    dir_project_root=dir_project_root,
)
