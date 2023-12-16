# -*- coding: utf-8 -*-

"""
.. note::

    This module has zero dependencies.
"""
import subprocess

from . import paths

def setup_virtualenv():
    print(f"🐍 Create virtualenv at {paths.dir_venv}")
    if paths.path_caller_virtualenv.exists() is False:
        args = [
            f"{paths.path_caller_pip}",
            "install",
            "virtualenv"
        ]
        subprocess.run(args, check=True)

    if paths.dir_venv.exists() is False:
        args = [
            f"{paths.path_caller_virtualenv}",
            "-p",
            f"{paths.path_caller_python}",
            f"{paths.dir_venv}"
        ]
        subprocess.run(args, check=True)
    print("  ✅ Done")

    print(f"💾 Install necessary dependencies in virtualenv")
    args = [
        f"{paths.path_bin_pip}",
        "install",
        "-q",
        "-r",
        f"{paths.path_requirements_txt}"
    ]
    subprocess.run(args, check=True)
    print("  ✅ Done")


def new_project(seed: str):
    """
    Create a new project based on a seed project.

    This function will create the virtualenv and install necessary dependencies
    if they don't exist. And then use the virtualenv's Python to run the
    CLI command, which actually calls the logic in ``pylib.cookiecutter_wrapper.new_project``.
    """
    setup_virtualenv()
    args = [
        f"{paths.path_bin_python}",
        f"{paths.path_cli}",
        "new",
        "--seed",
        seed,
    ]
    subprocess.run(args, check=True)
