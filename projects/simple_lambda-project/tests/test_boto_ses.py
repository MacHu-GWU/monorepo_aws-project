# -*- coding: utf-8 -*-

from simple_lambda.boto_ses import boto_ses


def test():
    _ = boto_ses.get_devops_bsm().aws_account_id
    _ = boto_ses.get_app_bsm().aws_account_id
    _ = boto_ses.get_devops_bsm().aws_account_id


if __name__ == "__main__":
    from simple_lambda.tests import run_cov_test

    run_cov_test(__file__, "simple_lambda.boto_ses", preview=False)
