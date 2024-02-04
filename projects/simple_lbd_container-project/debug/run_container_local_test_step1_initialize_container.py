# -*- coding: utf-8 -*-

"""
This script runs lambda function container locally for testing purpose.
It will host the lambda function on port localhost:9000.

Then you can run ``run_container_local_test_step2_run_test.py`` script to test
the lambda function locally. Afterwards, you can run
``run_container_local_test_step3_stop_container.py`` to stop the container.

Reference:

- Using an AWS base image for Python - (Optional) Test the image locally: https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions
"""

import os
import subprocess

from simple_lbd_container.pyproject import pyproject_ops
from simple_lbd_container.config.api import config
from simple_lbd_container.boto_ses import boto_ses_factory

# Set linux/amd64 for x86, set linux/arm64 for arm
os.environ["DOCKER_DEFAULT_PLATFORM"] = "linux/amd64"


def initialize_lambda_container():
    bsm_app = boto_ses_factory.bsm_app
    credential = bsm_app.boto_ses.get_credentials()
    env_vars = {
        "AWS_REGION": bsm_app.aws_region,
        "AWS_DEFAULT_REGION": bsm_app.aws_region,
        "AWS_ACCESS_KEY_ID": credential.access_key,
        "AWS_SECRET_ACCESS_KEY": credential.secret_key,
        "AWS_SESSION_TOKEN": credential.token,
        "USER_ENV_NAME": config.env.env_name,
        "PARAMETER_NAME": config.env.parameter_name,
    }
    env_vars.update(config.env.env_vars)
    args = [
        "docker",
        "run",
        "--rm",
        "--name",
        f"{pyproject_ops.package_name}_lambda_container_local_test",
        "-p",
        "9000:8080",
    ]
    for k, v in env_vars.items():
        if v is not None:
            args.extend(["-e", f"{k}={v}"])
    args.append(
        config.env.get_ecr_repo_uri(
            bsm_devops=boto_ses_factory.bsm_devops,
            tag="latest",
        )
    )
    # print(" ".join(args))
    # print("\n\t".join(args))
    subprocess.run(args=args, check=True)


if __name__ == "__main__":
    initialize_lambda_container()
