# -*- coding: utf-8 -*-

"""
This module implements the automation to deploy CloudFormation stack via CDK.
"""

# standard library
import typing as T
from pathlib import Path

# third party library (include vendor)
import aws_console_url.api as aws_console_url
from ...vendor.emoji import Emoji

# modules from this project
from ...logger import logger
from ...aws_helpers import aws_cdk_helpers
from ...vendor import semantic_branch as sem_branch

# modules from this submodule
from .constants import StepEnum, GitBranchNameEnum, EnvNameEnum
from .rule import RuleSet, rule_set as default_rule_set

# type hint
if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager


semantic_branch_rules = {
    GitBranchNameEnum.main: ["main", "master"],
    GitBranchNameEnum.feature: ["feature", "feat"],
    GitBranchNameEnum.fix: ["fix"],
    GitBranchNameEnum.doc: ["doc"],
    GitBranchNameEnum.app: ["app"],
    GitBranchNameEnum.release: ["release", "rls"],
    GitBranchNameEnum.cleanup: ["cleanup", "clean"],
}

semantic_branch_rule = sem_branch.SemanticBranchRule(
    rules=semantic_branch_rules,
)

@logger.emoji_block(
    msg="Run 'cdk deploy'",
    emoji=Emoji.cloudformation,
)
def cdk_deploy(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    bsm_workload: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
    check: bool = True,
    rule_set: RuleSet = default_rule_set,
):  # pragma: no cover
    """
    Run ``cdk deploy ...`` command.
    """
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.DEPLOY_CDK_STACK,
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return
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
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    bsm_workload: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
    check: bool = True,
    rule_set: RuleSet = default_rule_set,
):  # pragma: no cover
    """
    Run ``cdk destroy ...`` command.
    """
    if check:
        _mapper = {
            EnvNameEnum.devops.value: StepEnum.DELETE_CDK_STACK_IN_SBX.value,
            EnvNameEnum.sbx.value: StepEnum.DELETE_CDK_STACK_IN_SBX.value,
            EnvNameEnum.tst.value: StepEnum.DELETE_CDK_STACK_IN_TST.value,
            EnvNameEnum.stg.value: StepEnum.DELETE_CDK_STACK_IN_STG.value,
            EnvNameEnum.prd.value: StepEnum.DELETE_CDK_STACK_IN_PRD.value,
        }
        flag = rule_set.should_we_do_it(
            step=StepEnum.DEPLOY_CDK_STACK,
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return
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
