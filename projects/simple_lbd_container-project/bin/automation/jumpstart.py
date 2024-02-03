# -*- coding: utf-8 -*-

import subprocess

try:
    from .pyproject import pyproject_ops
except ImportError:
    from .paths import path_requirements_jumpstart_txt, path_bin_pip

    args = [
        f"{path_bin_pip}",
        "install",
        "-r",
        f"{path_requirements_jumpstart_txt}",
    ]
    print(" ".join(args))
    subprocess.run(args, check=True)

    from .pyproject import pyproject_ops
