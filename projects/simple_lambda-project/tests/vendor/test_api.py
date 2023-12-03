# -*- coding: utf-8 -*-

from simple_lambda.vendor.aws_ops_alpha import api


def test():
    _ = api


if __name__ == "__main__":
    from simple_lambda.vendor.aws_ops_alpha.tests import run_cov_test

    run_cov_test(__file__, "simple_lambda.vendor.aws_ops_alpha.api", preview=False)
