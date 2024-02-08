#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from simple_glue.ops import pip_install_awsglue

    pip_install_awsglue()
except ImportError:
    import subprocess
    from automation.api import pyproject_ops

    args = [
        f"{pyproject_ops.path_venv_bin_pip}",
        "install",
        # make sure your glue version align with the config.env_name.glue_jobs.job_name.glue_version
        "git+https://github.com/awslabs/aws-glue-libs.git@v4.0",
    ]
    subprocess.run(args)
