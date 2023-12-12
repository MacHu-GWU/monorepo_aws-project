# -*- coding: utf-8 -*-

from simple_lambda.env import EnvNameEnum, detect_current_env


def test():
    _ = detect_current_env()


if __name__ == "__main__":
    from simple_lambda.tests import run_cov_test

    run_cov_test(__file__, "simple_lambda.env", preview=False)
