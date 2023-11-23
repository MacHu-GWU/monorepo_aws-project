# -*- coding: utf-8 -*-

import subprocess

from ..config_init import config
from ..paths import dir_venv, dir_bootstrap, bin_venv_pip


def main():
    args = [
        "virtualenv",
        "-p",
        f"python{config.python_version_major}.{config.python_version_minor}",
        f"{dir_venv}",
    ]
    subprocess.run(args, check=True)

    args = [
        f"{bin_venv_pip}",
        "install",
        "-r",
        str(dir_bootstrap.joinpath("requirements.txt"))
    ]
    subprocess.run(args, check=True)
