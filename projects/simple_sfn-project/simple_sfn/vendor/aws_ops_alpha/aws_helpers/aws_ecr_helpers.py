# -*- coding: utf-8 -*-

"""
This module implements the automation to build and push container image for ECR.
"""

# --- standard library
import typing as T

# --- third party library (include vendor)
from pathlib import Path
from ..vendor.aws_ecr import (
    ecr_login as _ecr_login,
    EcrContext,
)

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager


def ecr_login(bsm_devops: "BotoSesManager"): # pragma: no cover
    """
    Login to ECR.

    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    """
    return _ecr_login(bsm_devops)


def build_image(
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    repo_name: str,
    path_dockerfile: Path,
    use_arm: bool = False,
): # pragma: no cover
    """
    Build container image using ``docker build`` command.

    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param repo_name: ECR repository name.
    :param path_dockerfile: Path to the ``Dockerfile``.
    :param use_arm: is True, then build for ARM architecture, otherwise build for x86_64.
    """
    ecr_context = EcrContext.new(
        bsm=bsm_devops,
        repo_name=repo_name,
        path_dockerfile=path_dockerfile,
    )
    additional_args = []
    if use_arm:
        additional_args.append("--platform=linux/arm64")
    else:
        additional_args.append("--platform=linux/amd64")
    ecr_context.build_image(
        image_tag_list=["latest", pyproject_ops.package_version],
        # Reference: https://docs.docker.com/engine/reference/commandline/build/#build-arg
        additional_args=additional_args,
    )


def push_image(
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    repo_name: str,
    path_dockerfile: Path,
): # pragma: no cover
    """
    Push built container image from local to ECR using ``docker build`` command.

    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param repo_name: ECR repository name.
    :param path_dockerfile: Path to the ``Dockerfile``.
    """
    ecr_login(bsm_devops)
    ecr_context = EcrContext.new(
        bsm=bsm_devops,
        repo_name=repo_name,
        path_dockerfile=path_dockerfile,
    )
    ecr_context.push_image(
        image_tag_list=["latest", pyproject_ops.package_version],
    )
