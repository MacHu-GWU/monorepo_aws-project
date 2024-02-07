# -*- coding: utf-8 -*-

"""
This module implements the automation to deploy CloudFormation stacks via CDK.
"""

# --- standard library
import subprocess
from pathlib import Path

# --- third party library (include vendor)
from boto_session_manager import PATH_DEFAULT_SNAPSHOT, BotoSesManager
from ..vendor.better_pathlib import temp_cwd

# --- modules from this project
from ..constants import EnvVarNameEnum
from ..env_var import temp_env_var


def cdk_deploy(
    bsm_devops: "BotoSesManager",
    bsm_workload: "BotoSesManager",
    dir_cdk: Path,
    env_name: str,
    path_bsm_devops_snapshot: Path = PATH_DEFAULT_SNAPSHOT,
    skip_prompt: bool = False,
):  # pragma: no cover
    """
    Run ``cdk deploy ...`` terminal command.

    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param bsm_workload: the workload AWS Account boto session manager.
    :param dir_cdk: the CDK directory, there should be an app.py and cdk.json file in it.
    :param env_name: environment name you want to deploy CloudFormation to.
    :param path_bsm_devops_snapshot: the path to a local json file, which
        contains the snapshot of the devops ``BotoSesManager`` object.
    :param skip_prompt: if True, skip cdk prompt.
    """
    with bsm_devops.temp_snapshot(path=path_bsm_devops_snapshot):
        with bsm_workload.awscli():
            with temp_env_var({EnvVarNameEnum.USER_ENV_NAME.value: env_name}):
                args = ["cdk", "deploy"]
                if skip_prompt is True:
                    args.extend(["--require-approval", "never"])
                with temp_cwd(dir_cdk):
                    subprocess.run(args, check=True)


def cdk_destroy(
    bsm_devops: "BotoSesManager",
    bsm_workload: "BotoSesManager",
    env_name: str,
    dir_cdk: Path,
    path_bsm_devops_snapshot: Path = PATH_DEFAULT_SNAPSHOT,
    skip_prompt: bool = False,
):  # pragma: no cover
    """
    Run ``cdk destroy ...`` terminal command.

    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param bsm_workload: the workload AWS Account ``BotoSesManager`` object.
    :param dir_cdk: the CDK directory, there should be an app.py and cdk.json file in it.
    :param env_name: environment name you want to deploy CloudFormation to.
    :param path_bsm_devops_snapshot: the path to a local json file, which
        contains the snapshot of the devops ``BotoSesManager`` object.
    :param skip_prompt: if True, skip cdk prompt.
    """
    with bsm_devops.temp_snapshot(path=path_bsm_devops_snapshot):
        with bsm_workload.awscli():
            with temp_env_var({EnvVarNameEnum.USER_ENV_NAME.value: env_name}):
                args = ["cdk", "destroy"]
                if skip_prompt is True:
                    args.extend(["--force"])
                with temp_cwd(dir_cdk):
                    subprocess.run(args, check=True)
