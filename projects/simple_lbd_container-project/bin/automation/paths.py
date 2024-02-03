# -*- coding: utf-8 -*-

import sys
from pathlib import Path

dir_bin = Path(__file__).absolute().parent.parent
dir_project_root = dir_bin.parent
path_pyproject_toml = dir_project_root.joinpath("pyproject.toml")
path_requirements_jumpstart_txt = dir_bin / "requirements-jumpstart.txt"
path_bin_pip = Path(sys.executable).parent / "pip"
