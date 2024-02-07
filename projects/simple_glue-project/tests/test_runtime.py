# -*- coding: utf-8 -*-

from simple_glue.runtime import runtime


def test():
    _ = runtime


if __name__ == "__main__":
    from simple_glue.tests import run_cov_test

    run_cov_test(__file__, "simple_glue.runtime", preview=False)
