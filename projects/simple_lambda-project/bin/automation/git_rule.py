# -*- coding: utf-8 -*-

from .rule_lib import only_do_on_certain_branch
from .logger import logger
from .emoji import Emoji


def do_we_create_git_tag(
    is_ci_runtime: bool,
    env_name: str,
    prod_env_name: str,
    branch_name: str,
    is_release_branch: bool,
) -> bool:
    """
    Check if we should run unit test or coverage test.

    Only run this after you just released a new version to production from CI.
    So you should create a new git tag on the commit.

    In CI, we only run unit test when it is a branch that may change the
    application code.
    """
    if is_ci_runtime:
        if env_name != prod_env_name:
            logger.info(
                f"{Emoji.red_circle} we ONLY create new git tag "
                f"on {prod_env_name!r} environment after successful deployment, "
                f"now it is {env_name!r} environment."
            )
            return False

        return only_do_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=[(is_release_branch, "release")],
            action="create git tag",
            runtime_name="CI",
        )
    else:  # always don't create git tag on local
        logger.info(
            f"{Emoji.red_circle} we ONLY create new git tag in CI runtime "
            f"on {prod_env_name!r} environment after successful deployment. "
            f"now it is {env_name!r} environment. "
            f"probably you are not in CI runtime?"
        )
        return False
