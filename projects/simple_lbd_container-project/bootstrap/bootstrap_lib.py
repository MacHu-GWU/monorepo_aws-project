#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python library for bootstrap automation. This library is designed to be
having zero dependencies.
"""

import os
import subprocess
from pathlib import Path

dir_here = Path(__file__).absolute().parent
dir_venv = dir_here / ".venv"
dir_venv_bin = dir_venv / "bin"
path_venv_bin_python = dir_venv_bin / "python"
path_venv_bin_pip = dir_venv_bin / "pip"

path_bootstrap_cli_py = dir_here.joinpath("bootstrap_cli.py")


def create_virtualenv():
    args = [
        "virtualenv",
        "-p",
        "python3.9",
        f"{dir_venv}",
    ]
    subprocess.run(args, check=True)


def install_dependencies():
    args = [
        f"{path_venv_bin_pip}",
        "install",
        "--quiet",
        "-r",
        str(dir_here.joinpath("requirements.txt")),
    ]
    subprocess.run(args, check=True)


def run_cdk_deploy():
    dir_cwd = os.getcwd()
    os.chdir(dir_here)
    args = [f"{path_venv_bin_python}", f"{path_bootstrap_cli_py}", "deploy"]
    subprocess.run(args, check=True)
    os.chdir(dir_cwd)


def run_cdk_destroy():
    dir_cwd = os.getcwd()
    os.chdir(dir_here)
    args = [f"{path_venv_bin_python}", f"{path_bootstrap_cli_py}", "delete"]
    subprocess.run(args, check=True)
    os.chdir(dir_cwd)
