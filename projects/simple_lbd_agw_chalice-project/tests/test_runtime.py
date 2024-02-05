# -*- coding: utf-8 -*-

from simple_lbd_agw_chalice.runtime import runtime


def test():
    _ = runtime


if __name__ == "__main__":
    from simple_lbd_agw_chalice.tests import run_cov_test

    run_cov_test(__file__, "simple_lbd_agw_chalice.runtime", preview=False)
