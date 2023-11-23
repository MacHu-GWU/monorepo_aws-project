# -*- coding: utf-8 -*-

"""
This module implements the automation to deploy CloudFormation stack via CDK.
"""

import typing as T
import os
import subprocess
from pathlib_mate import Path

from .aws_console import get_aws_console
from .logger import logger
from .emoji import Emoji

if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager


@logger.start_and_end(
    msg="Run 'cdk deploy'",
    start_emoji=Emoji.cloudformation,
    error_emoji=f"{Emoji.failed} {Emoji.cloudformation}",
    end_emoji=f"{Emoji.succeeded} {Emoji.cloudformation}",
    pipe=Emoji.cloudformation,
)
def cdk_deploy(
    env_name: str,
    bsm: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str
):
    """
    Run ``cdk deploy ...`` command.
    """
    logger.info(f"deploy cloudformation to {env_name!r} env ...")
    aws_console = get_aws_console(bsm=bsm)
    url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {url}")
    with bsm.awscli():
        os.environ["USER_ENV_NAME"] = env_name
        args = [
            "cdk",
            "deploy",
            "--require-approval",
            "never",
        ]
        with dir_cdk.temp_cwd():
            subprocess.run(args, check=True)


@logger.start_and_end(
    msg="Run 'cdk destroy'",
    start_emoji=Emoji.cloudformation,
    error_emoji=f"{Emoji.failed} {Emoji.cloudformation}",
    end_emoji=f"{Emoji.succeeded} {Emoji.cloudformation}",
    pipe=Emoji.cloudformation,
)
def cdk_destroy(
    env_name: str,
    bsm: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
):
    """
    Run ``cdk destroy ...`` command.
    """
    logger.info(f"delete cloudformation from {env_name!r} env ...")
    aws_console = get_aws_console(bsm=bsm)
    url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {url}")
    with bsm.awscli():
        os.environ["USER_ENV_NAME"] = env_name
        args = [
            "cdk",
            "destroy",
            "--force",
        ]
        with dir_cdk.temp_cwd():
            subprocess.run(args, check=True)
