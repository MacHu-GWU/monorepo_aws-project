# -*- coding: utf-8 -*-

from pathlib import Path

dir_bootstrap = Path(__file__).absolute().parent.parent
path_config = dir_bootstrap / "config.json"
dir_venv = dir_bootstrap / ".venv"
bin_venv_python = dir_venv / "bin" / "python"
bin_venv_pip = dir_venv / "bin" / "pip"
path_cli = dir_bootstrap / "cli.py"
