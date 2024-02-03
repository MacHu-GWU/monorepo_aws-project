# -*- coding: utf-8 -*-

from simple_lbd_container.runtime import runtime


def test():
    _ = runtime


if __name__ == "__main__":
    from simple_lbd_container.tests import run_cov_test

    run_cov_test(__file__, "simple_lbd_container.runtime", preview=False)
