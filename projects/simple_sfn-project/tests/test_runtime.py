# -*- coding: utf-8 -*-

from simple_sfn.runtime import runtime


def test():
    _ = runtime


if __name__ == "__main__":
    from simple_sfn.tests import run_cov_test

    run_cov_test(__file__, "simple_sfn.runtime", preview=False)
