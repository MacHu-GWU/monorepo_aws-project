# -*- coding: utf-8 -*-

from simple_sfn.env import EnvNameEnum, detect_current_env


def test():
    _ = detect_current_env()


if __name__ == "__main__":
    from simple_sfn.tests import run_cov_test

    run_cov_test(__file__, "simple_sfn.env", preview=False)
