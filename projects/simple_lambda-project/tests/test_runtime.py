# -*- coding: utf-8 -*-

from simple_lambda.runtime import runtime


def test():
    _ = runtime


if __name__ == "__main__":
    from simple_lambda.tests import run_cov_test

    run_cov_test(__file__, "simple_lambda.runtime", preview=False)
