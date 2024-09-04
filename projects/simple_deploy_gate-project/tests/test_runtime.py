# -*- coding: utf-8 -*-

from simple_deploy_gate.runtime import runtime


def test():
    _ = runtime


if __name__ == "__main__":
    from simple_deploy_gate.tests import run_cov_test

    run_cov_test(__file__, "simple_deploy_gate.runtime", preview=False)
