#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script is used to set up the virtual environment in GitHub Action CI.
We use global Python to run this script (because the project venv is not ready yet).

It leverages the cache to restore the venv from the previous run if the poetry.lock
file is not changed.
"""

import os
import subprocess
from pathlib import Path

dir_here = Path(__file__).absolute().parent
dir_project_root = dir_here.parent
dir_venv = dir_project_root / ".venv"
path_venv_bin_poetry = dir_venv / "bin" / "poetry"

os.chdir(f"{dir_project_root}")

# if venv does not exist (recover from cache),  create it.
if dir_venv.exists() is False:
    subprocess.run(
        [
            "virtualenv",
            "-p",
            "python3.9",
            ".venv",
        ]
    )

# if the poetry CLI entry point file does not exist, which means that
# we haven't run "poetry install" yet, we run it.
if path_venv_bin_poetry.exists() is False:
    subprocess.run(
        [
            f"poetry",
            "install",
            "--with",
            "dev,doc,test,auto",
        ],
        check=True,
    )
