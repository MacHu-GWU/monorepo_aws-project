# -*- coding: utf-8 -*-

from .rule_lib import only_do_on_certain_branch
from .logger import logger
from .emoji import Emoji


def do_we_run_unit_test(
    is_ci_runtime: bool,
    branch_name: str,
    is_master_branch: bool,
    is_feature_branch: bool,
    is_fix_branch: bool,
    is_ecr_branch: bool,
    is_lambda_branch: bool,
    is_release_branch: bool,
) -> bool:
    """
    Check if we should run unit test or coverage test.
    """
    if is_ci_runtime:
        return only_do_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=[
                (is_master_branch, "master"),
                (is_feature_branch, "feature"),
                (is_fix_branch, "fix"),
                (is_ecr_branch, "ecr"),
                (is_lambda_branch, "lambda"),
                (is_release_branch, "release"),
            ],
            action="run unit test",
            runtime_name="CI",
        )
    else:  # always run unit test on Local
        return True


def do_we_run_int_test(
    env_name: str,
    prod_env_name: str,
    is_ci_runtime: bool,
    branch_name: str,
    is_master_branch: bool,
    is_lambda_branch: bool,
    is_release_branch: bool,
) -> bool:
    """
    Check if we should run integration test.

    In CI, we only run integration test when it is a branch that deploy the app.

    There's an exception that, we don't run unit test in prod environment
    because integration test may change the state of the cloud resources,
    and it should be already thoroughly tested in previous environments.
    """
    if is_ci_runtime:
        if env_name == prod_env_name:
            logger.info(
                f"{Emoji.red_circle} don't run integration test "
                f"on {prod_env_name!r} environment, "
                "It should be thoroughly tested in previous environments."
                f"now it is {env_name!r} environment."
            )
            return False

        return only_do_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=[
                (is_master_branch, "master"),
                (is_lambda_branch, "lambda"),
                (is_release_branch, "release"),
            ],
            action="run integration test",
            runtime_name="CI",
        )
    else:  # always run int test on Local
        return True
