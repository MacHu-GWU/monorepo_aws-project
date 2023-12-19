# -*- coding: utf-8 -*-

from simple_cdk2.env import EnvNameEnum, detect_current_env


def test():
    _ = detect_current_env()


if __name__ == "__main__":
    from simple_cdk2.tests import run_cov_test

    run_cov_test(__file__, "simple_cdk2.env", preview=False)
