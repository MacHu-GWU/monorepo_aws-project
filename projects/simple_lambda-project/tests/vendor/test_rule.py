# -*- coding: utf-8 -*-

from simple_lambda.vendor.aws_ops_alpha.rule import (
    only_execute_on_certain_branch,
    confirm_to_proceed_in_prod,
)


def test_confirm_to_proceed_in_prod():
    confirm_to_proceed_in_prod(
        prod_env_name="prd",
        action="deploy CDK stack",
        verbose=True,
    )
    assert (
        confirm_to_proceed_in_prod(
            prod_env_name="prd",
            action="deploy CDK stack",
            skip_prompt=False,
            _user_input="N",
        )
        is False
    )

    assert (
        confirm_to_proceed_in_prod(
            prod_env_name="prd",
            action="deploy CDK stack",
            skip_prompt=False,
            _user_input="YES",
        )
        is True
    )

    assert (
        confirm_to_proceed_in_prod(
            prod_env_name="prd",
            action="deploy CDK stack",
            skip_prompt=True,
        )
        is True
    )


def test_only_execute_on_certain_branch():
    assert (
        only_execute_on_certain_branch(
            branch_name="feature",
            flag_and_branches=[
                (True, "feat"),
                (True, "fix"),
            ],
            action="unit test",
            runtime_name="CI",
        )
        is True
    )

    assert (
        only_execute_on_certain_branch(
            branch_name="main",
            flag_and_branches=[
                (False, "release"),
            ],
            action="deploy to prod",
            runtime_name="CI",
        )
        is False
    )


if __name__ == "__main__":
    from simple_lambda.tests import run_cov_test

    run_cov_test(__file__, "simple_lambda.vendor.aws_ops_alpha.rule", preview=False)
