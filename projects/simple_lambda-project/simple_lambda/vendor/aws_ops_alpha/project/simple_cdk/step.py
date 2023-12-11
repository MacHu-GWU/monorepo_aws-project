# -*- coding: utf-8 -*-

"""
This module implements the automation to deploy CloudFormation stack via CDK.
"""

# standard library
import typing as T
import dataclasses
from pathlib import Path

# third party library (include vendor)
import aws_console_url.api as aws_console_url
from ...vendor.emoji import Emoji

# modules from this project
from ...logger import logger
from ...aws_helpers import aws_cdk_helpers

# type hint
if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager


@logger.emoji_block(
    msg="Run 'cdk deploy'",
    emoji=Emoji.cloudformation,
)
def cdk_deploy(
    bsm_workload: "BotoSesManager",
    env_name: str,
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
):
    """
    Run ``cdk deploy ...`` command.
    """
    logger.info(f"deploy cloudformation to {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {url}")
    aws_cdk_helpers.cdk_deploy(
        bsm_workload=bsm_workload,
        env_name=env_name,
        dir_cdk=dir_cdk,
        skip_prompt=skip_prompt,
    )

@logger.emoji_block(
    msg="Run 'cdk destroy'",
    emoji=Emoji.cloudformation,
)
def cdk_destroy(
    bsm_workload: "BotoSesManager",
    env_name: str,
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
):
    """
    Run ``cdk destroy ...`` command.
    """
    logger.info(f"delete cloudformation from {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {url}")
    aws_cdk_helpers.cdk_destroy(
        bsm_workload=bsm_workload,
        env_name=env_name,
        dir_cdk=dir_cdk,
        skip_prompt=skip_prompt,
    )
