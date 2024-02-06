# -*- coding: utf-8 -*-

"""
Build lambda layer and create a zip file.

**IMPORTANT**

THIS SHELL SCRIPT HAS TO BE EXECUTED IN THE CONTAINER, NOT IN THE HOST MACHINE.
"""

import subprocess
from pathlib import Path

# verify the current runtime
dir_here = Path(__file__).absolute().parent
if str(dir_here) != "/var/task":
    raise EnvironmentError(
        "This script has to be executed in the container, not in the host machine"
    )

# install aws_lambda_layer
args = ["pip", "install", "aws_lambda_layer>=0.5.1,<1.0.0"]
subprocess.run(args)

# build the lambda layer
# the "build lambda layer" automation logics is based on the
# aws_lambda_layer (https://github.com/MacHu-GWU/aws_lambda_layer-project)
# Python library
import aws_lambda_layer.api as aws_lambda_layer

dir_root = dir_here
layer_sha256 = aws_lambda_layer.build_layer_artifacts(
    path_requirements=dir_root / "requirements.txt",
    dir_build=dir_root / "build" / "lambda",
    bin_pip="/var/lang/bin/pip",
    quiet=False,
)
