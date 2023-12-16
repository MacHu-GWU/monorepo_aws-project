# -*- coding: utf-8 -*-

from simple_cdk1.env import EnvNameEnum, detect_current_env


def test():
    _ = detect_current_env()


if __name__ == "__main__":
    from simple_cdk1.tests import run_cov_test

    run_cov_test(__file__, "simple_cdk1.env", preview=False)
