# -*- coding: utf-8 -*-

"""
This module implements the automation to deploy CloudFormation stack via CDK.
"""

import typing as T
import subprocess
from pathlib import Path

from ..vendor.better_pathlib import temp_cwd

from ..constants import EnvVarNameEnum
from ..env_var import temp_env_var

if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager


def cdk_deploy(
    bsm_workload: "BotoSesManager",
    dir_cdk: Path,
    env_name: str,
    skip_prompt: bool = False,
):  # pragma: no cover
    """
    Run ``cdk deploy ...`` command.
    """
    # with bsm_workload.awscli():
    with temp_env_var({EnvVarNameEnum.USER_ENV_NAME.value: env_name}):
        args = ["cdk", "deploy", "--role-arn", "arn:aws:iam::878625312159:role/monorepo_aws-sbx-deployer-us-east-1"]
        # args = ["cdk", "deploy"]
        if skip_prompt is True:
            args.extend(["--require-approval", "never"])
        with temp_cwd(dir_cdk):
            subprocess.run(args, check=True)


def cdk_destroy(
    bsm_workload: "BotoSesManager",
    env_name: str,
    dir_cdk: Path,
    skip_prompt: bool = False,
):  # pragma: no cover
    """
    Run ``cdk destroy ...`` command.
    """
    with bsm_workload.awscli():
        with temp_env_var({EnvVarNameEnum.USER_ENV_NAME.value: env_name}):
            args = ["cdk", "destroy"]
            if skip_prompt is True:
                args.extend(["--force"])
            with temp_cwd(dir_cdk):
                subprocess.run(args, check=True)
