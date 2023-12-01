#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
from pathlib import Path

dir_here = Path(__file__).absolute().parent
dir_project_root = dir_here.parent
dir_venv = dir_project_root / ".venv"
path_venv_bin_pip = dir_venv / "bin" / "pip"

os.chdir(f"{dir_project_root}")

if dir_venv.exists() is False:
    subprocess.run(
        [
            "virtualenv",
            "-p",
            "python3.9",
            ".venv",
        ]
    )

    subprocess.run(
        [
            f"{path_venv_bin_pip}",
            "install",
            "-e",
            f"{dir_project_root}",
            "--no-deps",
        ],
        check=True,
    )

    for path in [
        dir_project_root.joinpath("requirements.txt"),
        dir_project_root.joinpath("requirements-dev.txt"),
        dir_project_root.joinpath("requirements-test.txt"),
        dir_project_root.joinpath("requirements-doc.txt"),
        dir_project_root.joinpath("requirements-automation.txt"),
    ]:
        subprocess.run(
            [f"{path_venv_bin_pip}", "install", "-r", f"{path}"],
            check=True,
        )
