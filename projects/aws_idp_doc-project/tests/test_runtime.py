# -*- coding: utf-8 -*-

from aws_idp_doc.runtime import runtime


def test():
    _ = runtime


if __name__ == "__main__":
    from aws_idp_doc.tests import run_cov_test

    run_cov_test(__file__, "aws_idp_doc.runtime", preview=False)
