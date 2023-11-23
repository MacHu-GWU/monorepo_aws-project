# -*- coding: utf-8 -*-

"""
Rule library for common logic to identify whether we should perform certain action.
"""

import typing as T

from .logger import logger
from .emoji import Emoji


def dummy_proof_for_prod(
    env_name: str,
    prod_env_name: str,
    action: str,
    skip_prompt: bool = False,
    yes_answer: str = "YES",
) -> bool:
    """
    Prompt to enter YES answer to proceed the action when you are trying to
    perform certain action to production environment.

    :param env_name: the environment you are working on
    :param prod_env_name: the production environment name
    :param action: the name of this action you want to perform
    :return: a boolean flag to indicate if we should do the action
    """
    if env_name == prod_env_name:
        if skip_prompt:
            return True
        user_input = input(
            f"you are trying to {action} to {prod_env_name!r} from local runtime, "
            f"enter '{yes_answer}' to confirm: "
        )
        if user_input.strip() == yes_answer:
            return True
        else:
            logger.info(
                f"{Emoji.red_circle} don't {action}. "
                f"because user input {user_input!r} is not '{yes_answer}'."
            )
            return False
    else:
        return True


def only_do_on_certain_branch(
    branch_name: str,
    flag_and_branches: T.List[T.Tuple[bool, str]],
    action: str,
    runtime_name: str,
) -> bool:
    """
    Only perform certain action on certain git branch.

    :param branch_name: current branch name
    :param flag_and_branches: a is_certain_branch and branch name pairs
    :param action: the name of this action you want to perform
    :param runtime_name: the name of the runtime you are working on, CI or local
    :return:
    """
    flags, branches = list(zip(*flag_and_branches))
    if any(flags):
        return True
    else:
        allowed_branches = " or ".join([f"{branch!r}" for branch in branches])
        logger.info(
            f"{Emoji.red_circle} don't {action}, "
            f"we only do it from {runtime_name} environment on "
            f"{allowed_branches} branch, "
            f"now we are on {branch_name!r} branch.",
        )
        return False
