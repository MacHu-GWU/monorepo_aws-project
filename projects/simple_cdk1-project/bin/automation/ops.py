# -*- coding: utf-8 -*-

import subprocess

try:
    from .pyproject import pyproject_ops
except ImportError:
    from .paths import path_requirements_jumpstart_txt, path_bin_pip

    subprocess.run(
        [
            f"{path_bin_pip}",
            "install",
            "-r",
            f"{path_requirements_jumpstart_txt}",
        ],
        check=True,
    )

    from .pyproject import pyproject_ops
