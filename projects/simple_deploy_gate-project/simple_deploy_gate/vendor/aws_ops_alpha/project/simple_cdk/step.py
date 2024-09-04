# -*- coding: utf-8 -*-

"""
This module implements the automation to deploy CloudFormation stack via CDK.

Developer note:

    every function in the ``step.py`` module should have visualized logging.
"""

# --- standard library
import typing as T
from pathlib import Path

# --- third party library (include vendor)
import aws_console_url.api as aws_console_url
import tt4human.api as tt4human
from ...vendor.emoji import Emoji

# --- modules from this project
from ...logger import logger
from ...aws_helpers import aws_cdk_helpers
from ...rule_set import should_we_do_it

#--- modules from this submodule
from .simple_cdk_truth_table import StepEnum, truth_table

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager


@logger.emoji_block(
    msg="Run 'cdk deploy'",
    emoji=Emoji.cloudformation,
)
def cdk_deploy(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    bsm_workload: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
    check: bool = True,
    step: str = StepEnum.deploy_cdk_stack.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Run ``cdk deploy ...`` terminal command.
    """
    logger.info(f"deploy cloudformation to {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    console_url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {console_url}")

    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return

    aws_cdk_helpers.cdk_deploy(
        bsm_devops=bsm_devops,
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
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    bsm_workload: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
    check: bool = True,
    step: str = StepEnum.delete_cdk_stack.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Run ``cdk destroy ...`` terminal command.
    """
    logger.info(f"delete cloudformation from {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    console_url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {console_url}")

    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return

    aws_cdk_helpers.cdk_destroy(
        bsm_devops=bsm_devops,
        bsm_workload=bsm_workload,
        env_name=env_name,
        dir_cdk=dir_cdk,
        skip_prompt=skip_prompt,
    )
