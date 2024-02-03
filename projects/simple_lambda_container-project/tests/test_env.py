# -*- coding: utf-8 -*-

from simple_lambda_container.env import EnvNameEnum, detect_current_env


def test():
    _ = detect_current_env()


if __name__ == "__main__":
    from simple_lambda_container.tests import run_cov_test

    run_cov_test(__file__, "simple_lambda_container.env", preview=False)
