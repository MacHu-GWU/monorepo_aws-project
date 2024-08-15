# -*- coding: utf-8 -*-

from dynamodbsnaplake.runtime import runtime


def test():
    _ = runtime


if __name__ == "__main__":
    from dynamodbsnaplake.tests import run_cov_test

    run_cov_test(__file__, "dynamodbsnaplake.runtime", preview=False)
