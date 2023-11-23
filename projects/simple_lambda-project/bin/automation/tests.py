# -*- coding: utf-8 -*-

import time

from .pyproject import pyproject_ops
from .runtime import IS_CI
from .git import (
    GIT_BRANCH_NAME,
    IS_MASTER_BRANCH,
    IS_FEATURE_BRANCH,
    IS_FIX_BRANCH,
    IS_ECR_BRANCH,
    IS_LAMBDA_BRANCH,
    IS_RELEASE_BRANCH,
)
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
    return do_we_run_unit_test(
        is_ci_runtime=IS_CI,
        branch_name=GIT_BRANCH_NAME,
        is_master_branch=IS_MASTER_BRANCH,
        is_feature_branch=IS_FEATURE_BRANCH,
        is_fix_branch=IS_FIX_BRANCH,
        is_ecr_branch=IS_ECR_BRANCH,
        is_lambda_branch=IS_LAMBDA_BRANCH,
        is_release_branch=IS_RELEASE_BRANCH,
    )


@logger.start_and_end(
    msg="Run Unit Test",
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

    pyproject_ops.run_unit_test()


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
