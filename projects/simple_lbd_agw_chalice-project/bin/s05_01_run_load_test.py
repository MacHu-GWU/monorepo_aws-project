# -*- coding: utf-8 -*-

import subprocess
from automation.api import pyproject_ops

path_bin_locust = pyproject_ops.dir_venv_bin / "locust"
path_locustfile = pyproject_ops.dir_tests_load / "locustfile_slow.py"

args = [
    f"{path_bin_locust}",
    "-f",
    f"{path_locustfile}",
    "--headless",
    "--users",
    "100",
    "--spawn-rate",
    "10",
    "--stop-timeout",
    "10",
]
subprocess.run(args)
