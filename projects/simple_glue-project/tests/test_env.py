# -*- coding: utf-8 -*-

from simple_glue.env import EnvNameEnum, detect_current_env


def test():
    _ = detect_current_env()


if __name__ == "__main__":
    from simple_glue.tests import run_cov_test

    run_cov_test(__file__, "simple_glue.env", preview=False)
