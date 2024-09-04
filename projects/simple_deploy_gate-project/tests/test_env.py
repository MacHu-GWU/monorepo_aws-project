# -*- coding: utf-8 -*-

from simple_deploy_gate.env import EnvNameEnum, detect_current_env


def test():
    _ = detect_current_env()


if __name__ == "__main__":
    from simple_deploy_gate.tests import run_cov_test

    run_cov_test(__file__, "simple_deploy_gate.env", preview=False)
