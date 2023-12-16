# -*- coding: utf-8 -*-

from .rule_lib import only_do_on_certain_branch, dummy_proof_for_prod


def do_we_deploy_app(
    env_name: str,
    prod_env_name: str,
    is_ci_runtime: bool,
    branch_name: str,
    is_master_branch: bool,
    is_lambda_branch: bool,
    is_release_branch: bool,
) -> bool:
    """
    Check if we should deploy app.
    """
    flag_and_branches = [
        (is_master_branch, "master"),
        (is_lambda_branch, "lambda"),
        (is_release_branch, "release"),
    ]
    action = "deploy app"
    if is_ci_runtime:
        return only_do_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=flag_and_branches,
            action=action,
            runtime_name="CI",
        )
    else:
        flag = only_do_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=flag_and_branches,
            action=action,
            runtime_name="local",
        )
        if flag is False:
            return False
        return dummy_proof_for_prod(
            env_name=env_name,
            prod_env_name=prod_env_name,
            action=action,
        )


def do_we_delete_app(
    env_name: str,
    prod_env_name: str,
    is_ci_runtime: bool,
    branch_name: str,
    is_cleanup_branch: bool,
) -> bool:
    """
    Check if we should delete app.
    """
    flag_and_branches = [
        (is_cleanup_branch, "cleanup"),
    ]
    action = "delete app"
    if is_ci_runtime:
        return only_do_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=flag_and_branches,
            action=action,
            runtime_name="CI",
        )
    else:
        flag = only_do_on_certain_branch(
            branch_name=branch_name,
            flag_and_branches=flag_and_branches,
            action=action,
            runtime_name="local",
        )
        if flag is False:
            return False
        return dummy_proof_for_prod(
            env_name=env_name,
            prod_env_name=prod_env_name,
            action=action,
        )
