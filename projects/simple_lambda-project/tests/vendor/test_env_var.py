# -*- coding: utf-8 -*-

import os
from simple_lambda.vendor.aws_ops_alpha.env_var import (
    get_devops_aws_account_id_in_ci,
    get_workload_aws_account_id_in_ci,
)


def test_get_devops_aws_account_id_in_ci():
    os.environ["DEVOPS_AWS_ACCOUNT_ID"] = "999999999999"
    assert get_devops_aws_account_id_in_ci() == "999999999999"


def test_get_workload_aws_account_id_in_ci():
    os.environ["SBX_AWS_ACCOUNT_ID"] = "111111111111"
    assert get_workload_aws_account_id_in_ci("sbx") == "111111111111"
    os.environ["TST_AWS_ACCOUNT_ID"] = "222222222222"
    assert get_workload_aws_account_id_in_ci("tst") == "222222222222"
    os.environ["PRD_AWS_ACCOUNT_ID"] = "333333333333"
    assert get_workload_aws_account_id_in_ci("prd") == "333333333333"


if __name__ == "__main__":
    from simple_lambda.tests import run_cov_test

    run_cov_test(__file__, "simple_lambda.vendor.aws_ops_alpha.env_var", preview=False)
