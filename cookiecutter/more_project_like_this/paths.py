# -*- coding: utf-8 -*-

from pathlib import Path

# ------------------------------------------------------------------------------
# Virtualenv related
# ------------------------------------------------------------------------------
dir_pylib = Path(__file__).absolute().parent
dir_cookiecutter = dir_pylib.parent

dir_venv = dir_cookiecutter.joinpath(".venv")
dir_bin = dir_venv.joinpath("bin")
path_bin_python = dir_bin.joinpath("python")
path_bin_pip = dir_bin.joinpath("pip")
path_bin_cookiecutter = dir_bin.joinpath("cookiecutter")

path_requirements_txt = dir_cookiecutter.joinpath("requirements.txt")

# ------------------------------------------------------------------------------
# Cookiecutter related
# ------------------------------------------------------------------------------
dir_project_root = dir_cookiecutter.parent
dir_tmp = dir_cookiecutter.joinpath("tmp")
dir_template_project = dir_tmp.joinpath("template-project")
dir_projects = dir_project_root.joinpath("projects")

path_cli = dir_cookiecutter.joinpath("cli.py")
