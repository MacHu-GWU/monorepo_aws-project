# -*- coding: utf-8 -*-

from simple_lambda.vendor.aws_ops_alpha.rule import (
    only_execute_on_certain_branch,
    only_execute_on_certain_runtime,
    only_execute_on_certain_env,
    confirm_to_proceed_in_prod,
)


def test_only_execute_on_certain_runtime():
    flag = only_execute_on_certain_runtime(
        runtime_name="ci",
        flag_and_runtimes=[
            (True, "ci"),
        ],
        action="unit test",
    )
    assert flag is True

    flag = only_execute_on_certain_runtime(
        runtime_name="local",
        flag_and_runtimes=[
            (False, "ci"),
        ],
        action="unit test",
    )
    assert flag is False


def test_only_execute_on_certain_branch():
    flag = only_execute_on_certain_branch(
        branch_name="ecr",
        flag_and_branches=[
            (True, "ecr"),
        ],
        action="build container image",
    )
    assert flag is True

    flag = only_execute_on_certain_branch(
        branch_name="eature",
        flag_and_branches=[
            (False, "ecr"),
        ],
        action="build container image",
    )
    assert flag is False


def test_only_execute_on_certain_env():
    flag = only_execute_on_certain_env(
        env_name="sbx",
        flag_and_envs=[
            (True, "sbx"),
            (True, "tst"),
        ],
        action="run integration test",
    )
    assert flag is True

    flag = only_execute_on_certain_env(
        env_name="prd",
        flag_and_envs=[
            (False, "sbx"),
            (False, "tst"),
        ],
        action="run integration test",
    )
    assert flag is False


def test_confirm_to_proceed_in_prod():
    flag = confirm_to_proceed_in_prod(
        prod_env_name="prd",
        action="deploy CDK stack",
        skip_prompt=False,
        _user_input="N",
    )
    assert flag is False

    flag = confirm_to_proceed_in_prod(
        prod_env_name="prd",
        action="deploy CDK stack",
        skip_prompt=False,
        _user_input="YES",
    )
    assert flag is True

    flag = confirm_to_proceed_in_prod(
        prod_env_name="prd",
        action="deploy CDK stack",
        skip_prompt=True,
    )
    assert flag is True


if __name__ == "__main__":
    from simple_lambda.tests import run_cov_test

    run_cov_test(__file__, "simple_lambda.vendor.aws_ops_alpha.rule", preview=False)
