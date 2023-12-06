# -*- coding: utf-8 -*-

import time

import aws_ops_alpha.api as aws_ops_alpha
from simple_lambda.git import git_repo

from .pyproject import pyproject_ops
from .env import CURRENT_ENV
from .logger import logger
from .emoji import Emoji
from .tests_rule import (
    do_we_run_unit_test,
    do_we_run_int_test,
)


def _do_we_run_unit_test() -> bool:
    """
    Code saver.
    """
    return aws_ops_alpha.simple_lambda.do_we_run_unit_test(
        is_ci_runtime=aws_ops_alpha.runtime.is_ci,
        branch_name=git_repo.git_branch_name,
        is_main_branch=git_repo.is_main_branch,
        is_feature_branch=git_repo.is_feature_branch,
        is_fix_branch=git_repo.is_fix_branch,
        is_layer_branch=git_repo.is_layer_branch,
        is_lambda_branch=git_repo.is_lambda_branch,
        is_release_branch=git_repo.is_release_branch,
    )


@logger(
    msg="Run Code Coverage Test",
    start_emoji=Emoji.test,
    error_emoji=f"{Emoji.failed} {Emoji.test}",
    end_emoji=f"{Emoji.succeeded} {Emoji.test}",
    pipe=Emoji.test,
)
def run_unit_test(
    check: bool = True,
):
    if check:
        if _do_we_run_unit_test() is False:
            return

    pyproject_ops.run_unit_test(verbose=True)


@logger.start_and_end(
    msg="Run Code Coverage Test",
    start_emoji=Emoji.test,
    error_emoji=f"{Emoji.failed} {Emoji.test}",
    end_emoji=f"{Emoji.succeeded} {Emoji.test}",
    pipe=Emoji.test,
)
def run_cov_test(
    check: bool = True,
):
    if check:
        if _do_we_run_unit_test() is False:
            return

    pyproject_ops.run_cov_test()


@logger.start_and_end(
    msg="View Code Coverage Test Result",
    start_emoji=Emoji.test,
    error_emoji=f"{Emoji.failed} {Emoji.test}",
    end_emoji=f"{Emoji.succeeded} {Emoji.test}",
    pipe=Emoji.test,
)
def view_cov():
    pyproject_ops.view_cov()


@logger.start_and_end(
    msg="Run Integration Test",
    start_emoji=Emoji.test,
    error_emoji=f"{Emoji.failed} {Emoji.test}",
    end_emoji=f"{Emoji.succeeded} {Emoji.test}",
    pipe=Emoji.test,
)
def run_int_test(
    prod_env_name: str,
    env_name: str = CURRENT_ENV,
    check: bool = True,
):
    logger.info(f"Run integration test in {env_name!r} env...")
    if check:
        if (
            do_we_run_int_test(
                env_name=env_name,
                prod_env_name=prod_env_name,
                is_ci_runtime=IS_CI,
                branch_name=GIT_BRANCH_NAME,
                is_master_branch=IS_MASTER_BRANCH,
                is_lambda_branch=IS_LAMBDA_BRANCH,
                is_release_branch=IS_RELEASE_BRANCH,
            )
            is False
        ):
            return

    if IS_CI:  # in CI, wait 5 seconds for infrastructure as code taking effect
        time.sleep(5)
    pyproject_ops.run_int_test()
