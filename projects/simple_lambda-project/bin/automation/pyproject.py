# -*- coding: utf-8 -*-

"""
Parse the ``pyproject.toml`` file.
"""

from pathlib_mate import Path
from pyproject_ops.api import PyProjectOps

dir_project_root = Path.dir_here(__file__).parent.parent
path_pyproject_toml = dir_project_root / "pyproject.toml"

pyproject_ops = PyProjectOps.from_pyproject_toml(path_pyproject_toml)
