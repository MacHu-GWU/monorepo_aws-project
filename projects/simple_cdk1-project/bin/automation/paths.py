# -*- coding: utf-8 -*-

import sys
from pathlib import Path

dir_automation = Path(__file__).absolute().parent
dir_bin = dir_automation.parent
path_requirements_jumpstart_txt = dir_bin.joinpath("requirements-jumpstart.txt")
dir_project_root = dir_automation.parent.parent
path_bin_pip = Path(sys.executable).parent.joinpath("pip")
