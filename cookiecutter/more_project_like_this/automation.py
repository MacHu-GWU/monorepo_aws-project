# -*- coding: utf-8 -*-

"""
.. note::

    This module has zero dependencies.
"""

import sys
import subprocess

from . import paths
from .virtualenv_bootstrap import Project


def new_project(seed: str):
    """
    Create a new project based on a seed project.

    This function will create the virtualenv and install necessary dependencies
    if they don't exist. And then use the virtualenv's Python to run the
    CLI command, which actually calls the logic in ``pylib.cookiecutter_wrapper.new_project``.
    """
    Project.new(
        path_python=sys.executable,
        dir_venv=paths.dir_venv,
        path_requirements_txt=paths.path_requirements_txt,
    )
    args = [
        f"{paths.path_bin_python}",
        f"{paths.path_cli}",
        "new",
        "--seed",
        seed,
    ]
    subprocess.run(args, check=True)
