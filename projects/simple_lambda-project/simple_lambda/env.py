# -*- coding: utf-8 -*-

import aws_ops_alpha.api as aws_ops_alpha

from .runtime import runtime

EnvEnum = aws_ops_alpha.EnvEnum


def detect_current_env() -> str:
    # ----------------------------------------------------------------------
    # you can uncomment this line to force to use certain env
    # from your local laptop to run application code, tests, ...
    # ----------------------------------------------------------------------
    # return EnvEnum.sbx.value
    return aws_ops_alpha.detect_current_env(runtime)
