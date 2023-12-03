# -*- coding: utf-8 -*-

"""
In the CI/CD workflow, we must execute numerous steps sequentially.
However, not all steps are necessary in every situation. For instance, we only
intend to execute the container image building step on specific git branches.
To achieve this, we should create a set of Python functions that accept
a git branch name as input and return a boolean flag to indicate whether
a particular action should be performed. This module offers utility tools
for implementing these functions.
"""

import typing as T

# it's OK to not using logging feature in this module
try:
    from .logger import logger
    from .emoji import Emoji
except ImportError:  # pragma: no cover
    pass


def only_execute_on_certain_branch(
    branch_name: str,
    flag_and_branches: T.List[T.Tuple[bool, str]],
    action: str,
    runtime_name: str,
    verbose: bool = False,
) -> bool:
    """
    Only perform certain action on certain git branch.

    Example:

        >>> only_execute_on_certain_branch(
        ...     branch_name="feature",
        ...     flag_and_branches=[
        ...         (True, "feature"),
        ...         (True, "fix"),
        ...     ],
        ...     action="unit test",
        ...     runtime_name="local",
        ... )
        True

    :param branch_name: current branch name.
    :param flag_and_branches: pairs of ``(is_certain_branch, branch_name)`` tuple
        if any of ``is_certain_branch`` flag is True, then we will execute the action,
        otherwise, we will skip the action.
    :param action: the name of this action you want to execute.
    :param runtime_name: the name of the runtime you are working on, CI or local.
    :param verbose: whether to print verbose logs we don't execute the action.

    :return: a boolean flag to indicate if we should do the action.
    """
    flags, branches = list(zip(*flag_and_branches))
    if any(flags):
        return True
    else:
        allowed_branches = " or ".join([f"{branch!r}" for branch in branches])
        if verbose:  # pragma: no cover
            logger.info(
                f"{Emoji.red_circle} don't {action}, "
                f"we only do it from {runtime_name} environment on "
                f"{allowed_branches} branch, "
                f"now we are on {branch_name!r} branch.",
            )
        return False


def confirm_to_proceed_in_prod(
    prod_env_name: str,
    action: str,
    skip_prompt: bool = False,
    yes_answer: str = "YES",
    verbose: bool = False,
    _user_input: T.Optional[str] = None,
) -> bool:
    """
    Prompt to enter YES answer to proceed the action when you are trying to
    perform certain action in production environment.

    We only need this for script running in local runtime, because there's no
    interactive prompt in CI runtime.

    Example:

        >>> confirm_to_proceed_in_prod(
        ... prod_env_name="prd",
        ... action="deploy CDK stack",
        ... skip_prompt=False,
        ... )
        you are trying to deploy CDK stack to 'prd' from local runtime, enter 'YES' to confirm: NO
        🔴 don't deploy CDK stack. because user input 'NO' is not 'YES'.

    :param prod_env_name: the production environment name.
    :param action: the name of this action you want to perform.
    :param skip_prompt: whether we should skip the prompt.
    :param yes_answer: the expected answer to proceed the action.
    :param verbose: whether to print verbose logs we don't execute the action.
    :param _user_input: an internal parameter for testing purpose.

    :return: a boolean flag to indicate if we should execute the action in production.
    """
    if skip_prompt:
        return True
    if _user_input is None:  # pragma: no cover
        user_input = input(
            f"you are trying to {action} to {prod_env_name!r} from local runtime, "
            f"enter '{yes_answer}' to confirm: "
        )
    else:
        user_input = _user_input
    if user_input.strip() == yes_answer:
        return True
    else:
        if verbose:  # pragma: no cover
            logger.info(
                f"{Emoji.red_circle} don't {action}. "
                f"because user input {user_input!r} is not '{yes_answer}'."
            )
        return False
