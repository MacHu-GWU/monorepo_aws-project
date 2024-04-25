# -*- coding: utf-8 -*-

from aws_idp_doc.env import EnvNameEnum, detect_current_env


def test():
    _ = detect_current_env()


if __name__ == "__main__":
    from aws_idp_doc.tests import run_cov_test

    run_cov_test(__file__, "aws_idp_doc.env", preview=False)
