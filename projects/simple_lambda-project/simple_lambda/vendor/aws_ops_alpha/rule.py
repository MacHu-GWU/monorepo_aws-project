# -*- coding: utf-8 -*-

"""
In the CI/CD workflow, we must execute numerous steps sequentially.
However, not all steps are necessary in every situation. For instance, we only
intend to execute the container image building step on specific git branches.
To achieve this, we should create a set of Python functions that accept
a git branch name as input and return a boolean flag to indicate whether
a particular action should be performed. This module offers utility tools
for implementing these functions.

Usage example::

    from rule import (
        only_execute_on_certain_branch,
        only_execute_on_certain_runtime,
        only_execute_on_certain_env,
        log_why_not_run_integration_test_in_prod,
        confirm_to_proceed_in_prod,
        only_execute_on_certain_runtime_branch_env,
        log_why_not_create_git_tag_in_non_prod,
        log_why_not_create_git_tag_in_local,
    )
"""

import typing as T

# it's OK to not using logging feature in this module
try:
    from .logger import logger
    from .emoji import Emoji
except ImportError:  # pragma: no cover
    pass


def only_execute_on_certain_runtime(
    runtime_name: str,
    flag_and_runtimes: T.List[T.Tuple[bool, str]],
    action: str,
    verbose: bool = False,
) -> bool:
    """
    Only perform certain action on certain runtime.

    Example:

        >>> only_execute_on_certain_runtime(
        ...     runtime_name="ci",
        ...     flag_and_runtimes=[
        ...         (True, "ci"),
        ...     ],
        ...     action="unit test",
        ... )
        True

    :param runtime_name: current runtime name.
    :param flag_and_runtimes: pairs of ``(is_certain_runtime, runtime_name)`` tuple
        if any of ``is_certain_runtime`` flag is True, then we will execute the action,
        otherwise, we will skip the action.
    :param action: the name of this action you want to execute.
    :param verbose: whether to print verbose logs we don't execute the action.

    :return: a boolean flag to indicate if we should do the action.
    """
    flags, runtimes = list(zip(*flag_and_runtimes))
    if any(flags):
        return True
    else:
        allowed_runtimes = " or ".join(
            [f"{runtime_name!r}" for runtime_name in runtimes]
        )
        if verbose:  # pragma: no cover
            logger.info(
                f"{Emoji.red_circle} don't {action}, "
                f"we only do it in {allowed_runtimes} runtime "
                f"now we are in {runtime_name!r} runtime.",
            )
        return False


def only_execute_on_certain_branch(
    branch_name: str,
    flag_and_branches: T.List[T.Tuple[bool, str]],
    action: str,
    verbose: bool = False,
) -> bool:
    """
    Only perform certain action on certain git branch.

    Example:

        >>> only_execute_on_certain_branch(
        ...     branch_name="ecr",
        ...     flag_and_branches=[
        ...         (True, "ecr"),
        ...     ],
        ...     action="build container image",
        ... )
        True

    :param branch_name: current branch name.
    :param flag_and_branches: pairs of ``(is_certain_branch, branch_name)`` tuple
        if any of ``is_certain_branch`` flag is True, then we will execute the action,
        otherwise, we will skip the action.
    :param action: the name of this action you want to execute.
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
                f"we only do it on {allowed_branches} branch, "
                f"now we are on {branch_name!r} branch.",
            )
        return False


def only_execute_on_certain_env(
    env_name: str,
    flag_and_envs: T.List[T.Tuple[bool, str]],
    action: str,
    verbose: bool = False,
) -> bool:
    """
    Only perform certain action on certain environments.

    Example:

        >>> only_execute_on_certain_env(
        ...     env_name="feature",
        ...     flag_and_envs=[
        ...         (True, "sbx"),
        ...         (True, "tst"),
        ...     ],
        ...     action="integration test",
        ... )
        True

    :param env_name: current environment name.
    :param flag_and_envs: pairs of ``(is_certain_env, env_name)`` tuple
        if any of ``is_certain_env`` flag is True, then we will execute the action,
        otherwise, we will skip the action.
    :param action: the name of this action you want to execute.
    :param verbose: whether to print verbose logs we don't execute the action.

    :return: a boolean flag to indicate if we should do the action.
    """
    flags, envs = list(zip(*flag_and_envs))
    if any(flags):
        return True
    else:
        allowed_envs = " or ".join([f"{env_name!r}" for env_name in envs])
        if verbose:  # pragma: no cover
            logger.info(
                f"{Emoji.red_circle} don't {action}, "
                f"we only do it on {allowed_envs} branch, "
                f"now we are on {env_name!r} environment.",
            )
        return False


def log_why_not_run_integration_test_in_prod(
    env_name: str,
    prod_env_name: str,
    verbose: bool = False,
):
    if verbose:
        logger.info(
            f"{Emoji.red_circle} don't run integration test "
            f"in {prod_env_name!r} environment, "
            "It should be thoroughly tested in previous environments."
            f"now it is {env_name!r} environment."
        )


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


def only_execute_on_certain_runtime_branch_env(
    action: str,
    runtime_name: T.Optional[str] = None,
    flag_and_runtimes: T.Optional[T.List[T.Tuple[bool, str]]] = None,
    branch_name: T.Optional[str] = None,
    flag_and_branches: T.Optional[T.List[T.Tuple[bool, str]]] = None,
    env_name: T.Optional[str] = None,
    flag_and_envs: T.Optional[T.List[T.Tuple[bool, str]]] = None,
    verbose: bool = False,
) -> bool:  # pragma: no cover
    """
    Only perform certain action on certain runtime, branch and environments.

    It is a combination of
    :func:`only_execute_on_certain_runtime`,
    :func:`only_execute_on_certain_branch`,
    :func:`only_execute_on_certain_env`.

    :return: a boolean flag to indicate if we should do the action.
    """
    if runtime_name:
        if (
            only_execute_on_certain_runtime(
                runtime_name=runtime_name,
                flag_and_runtimes=flag_and_runtimes,
                action=action,
                verbose=verbose,
            )
            is False
        ):
            return False

    if branch_name:
        if (
            only_execute_on_certain_branch(
                branch_name=branch_name,
                flag_and_branches=flag_and_branches,
                action=action,
                verbose=verbose,
            )
            is False
        ):
            return False

    if env_name:
        if (
            only_execute_on_certain_env(
                env_name=env_name,
                flag_and_envs=flag_and_envs,
                action=action,
                verbose=verbose,
            )
            is False
        ):
            return False

    return True


def log_why_not_create_git_tag_in_non_prod(
    env_name: str,
    prod_env_name: str,
    verbose: bool = False,
):
    if verbose:
        logger.info(
            f"{Emoji.red_circle} we ONLY create new git tag "
            f"on {prod_env_name!r} environment after successful deployment, "
            f"now it is {env_name!r} environment."
        )


def log_why_not_create_git_tag_in_local(
    env_name: str,
    prod_env_name: str,
    verbose: bool = False,
):
    if verbose:
        logger.info(
            f"{Emoji.red_circle} we ONLY create new git tag in CI runtime "
            f"on {prod_env_name!r} environment after successful deployment. "
            f"now it is {env_name!r} environment. "
            f"probably you are not in CI runtime?"
        )
        return False
