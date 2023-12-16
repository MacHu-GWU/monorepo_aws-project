# -*- coding: utf-8 -*-

from simple_cdk1.runtime import runtime


def test():
    _ = runtime


if __name__ == "__main__":
    from simple_cdk1.tests import run_cov_test

    run_cov_test(__file__, "simple_cdk1.runtime", preview=False)
