# -*- coding: utf-8 -*-

import typing as T
import time

import aws_ops_alpha.api as aws_ops_alpha

from ..logger import logger
from ..runtime import runtime
from ..git import git_repo
from ..env import get_current_env
from .pyproject import pyproject_ops
# from .emoji import Emoji
# from .tests_rule import (
#     do_we_run_unit_test,
#     do_we_run_int_test,
# )

Emoji = aws_ops_alpha.Emoji


def _do_we_run_unit_test() -> bool:
    """
    Code saver.
    """
    return aws_ops_alpha.simple_lambda.do_we_run_unit_test(
        is_ci_runtime=runtime.is_ci,
        branch_name=git_repo.git_branch_name,
        is_main_branch=git_repo.is_main_branch,
        is_feature_branch=git_repo.is_feature_branch,
        is_fix_branch=git_repo.is_fix_branch,
        is_layer_branch=git_repo.is_layer_branch,
        is_lambda_branch=git_repo.is_lambda_branch,
        is_release_branch=git_repo.is_release_branch,
    )


@logger.emoji_block(
    msg="Run Code Coverage Test",
    emoji=Emoji.test,
)
def run_unit_test(
    check: bool = True,
):
    if check:
        if _do_we_run_unit_test() is False:
            return

    pyproject_ops.run_unit_test()


@logger.emoji_block(
    msg="Run Code Coverage Test",
    emoji=Emoji.test,
)
def run_cov_test(
    check: bool = True,
):
    if check:
        if _do_we_run_unit_test() is False:
            return

    pyproject_ops.run_cov_test()


def view_cov():
    pyproject_ops.view_cov()


@logger.emoji_block(
    msg="Run Integration Test",
    emoji=Emoji.test,
)
def run_int_test(
    prod_env_name: str,
    env_name: T.Optional[str] = None,
    check: bool = True,
):
    if env_name is None:
        env_name = get_current_env()
    logger.info(f"Run integration test in {env_name!r} env...")
    if check:
        if (
            aws_ops_alpha.simple_lambda.do_we_run_int_test(
                env_name=env_name,
                prod_env_name=prod_env_name,
                is_ci_runtime=runtime.is_ci,
                branch_name=git_repo.git_branch_name,
                is_main_branch=git_repo.is_main_branch,
                is_lambda_branch=git_repo.is_lambda_branch,
                is_release_branch=git_repo.is_release_branch,
            )
            is False
        ):
            return

    if runtime.is_ci:  # in CI, wait 5 seconds for infrastructure as code taking effect
        time.sleep(5)
    pyproject_ops.run_int_test()
