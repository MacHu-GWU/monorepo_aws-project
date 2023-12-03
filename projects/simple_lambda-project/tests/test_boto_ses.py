# -*- coding: utf-8 -*-

from simple_lambda.config.define import EnvEnum
from simple_lambda.boto_ses import boto_ses_factory


def test():
    _ = boto_ses_factory.get_devops_bsm().aws_account_id
    _ = boto_ses_factory.get_app_bsm(EnvEnum.sbx).aws_account_id
    _ = boto_ses_factory.get_app_bsm(EnvEnum.tst).aws_account_id
    _ = boto_ses_factory.get_app_bsm(EnvEnum.prd).aws_account_id


if __name__ == "__main__":
    from simple_lambda.tests import run_cov_test

    run_cov_test(__file__, "simple_lambda.boto_ses", preview=False)
