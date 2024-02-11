# -*- coding: utf-8 -*-

from simple_sfn.boto_ses import boto_ses_factory


def test():
    _ = boto_ses_factory.get_current_env()

    _ = boto_ses_factory.bsm_devops.aws_account_alias
    _ = boto_ses_factory.bsm_sbx.aws_account_alias
    _ = boto_ses_factory.bsm_tst.aws_account_alias
    _ = boto_ses_factory.bsm_prd.aws_account_alias
    _ = boto_ses_factory.bsm_app.aws_account_alias

    # print(f"{boto_ses_factory.bsm_devops.aws_account_alias = }")
    # print(f"{boto_ses_factory.bsm_sbx.aws_account_alias = }")
    # print(f"{boto_ses_factory.bsm_tst.aws_account_alias = }")
    # print(f"{boto_ses_factory.bsm_prd.aws_account_alias = }")
    # print(f"{boto_ses_factory.bsm_app.aws_account_alias = }")

    for bsm in boto_ses_factory.workload_bsm_list:
        _ = bsm.aws_account_alias
        # print(f"{bsm.aws_account_alias = }")


if __name__ == "__main__":
    from simple_sfn.tests import run_cov_test

    run_cov_test(__file__, "simple_sfn.boto_ses", preview=False)
