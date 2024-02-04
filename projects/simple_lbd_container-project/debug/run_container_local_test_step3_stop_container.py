# -*- coding: utf-8 -*-

"""
Stop local test lambda function container.

Reference:

- Using an AWS base image for Python - (Optional) Test the image locally: https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions
"""

import subprocess
from simple_lbd_container.pyproject import pyproject_ops


def stop_lambda_container():
    args = [
        "docker",
        "stop",
        f"{pyproject_ops.package_name}_lambda_container_local_test",
    ]
    # print(" ".join(args))
    # print("\n\t".join(args))
    subprocess.run(args=args, check=True)


if __name__ == "__main__":
    stop_lambda_container()
