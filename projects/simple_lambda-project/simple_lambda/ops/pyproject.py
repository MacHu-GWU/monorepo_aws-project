# -*- coding: utf-8 -*-

"""
Create the PyProjectOps object,
The namespace for all the pyproject_ops automation methods.
"""

from pyproject_ops.api import PyProjectOps

from ..paths import dir_project_root

path_pyproject_toml = dir_project_root / "pyproject.toml"

pyproject_ops = PyProjectOps.from_pyproject_toml(path_pyproject_toml)
