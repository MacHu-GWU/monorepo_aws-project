# -*- coding: utf-8 -*-

import subprocess

args = [
    "docker", "container", "stop", "simple_glue_local_jupyter_lab_for_glue"
]
subprocess.run(args)
