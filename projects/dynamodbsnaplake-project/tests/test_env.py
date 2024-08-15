# -*- coding: utf-8 -*-

from dynamodbsnaplake.env import EnvNameEnum, detect_current_env


def test():
    _ = detect_current_env()


if __name__ == "__main__":
    from dynamodbsnaplake.tests import run_cov_test

    run_cov_test(__file__, "dynamodbsnaplake.env", preview=False)
