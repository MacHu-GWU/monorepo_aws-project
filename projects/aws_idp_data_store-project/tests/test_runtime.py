# -*- coding: utf-8 -*-

from aws_idp_data_store.runtime import runtime


def test():
    _ = runtime


if __name__ == "__main__":
    from aws_idp_data_store.tests import run_cov_test

    run_cov_test(__file__, "aws_idp_data_store.runtime", preview=False)
