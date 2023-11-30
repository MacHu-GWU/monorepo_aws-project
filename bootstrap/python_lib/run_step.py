# -*- coding: utf-8 -*-

import subprocess
from .paths import bin_venv_python, path_cli


def run_step(step_name: str):
    subprocess.run([f"{bin_venv_python}", f"{path_cli}", step_name])
