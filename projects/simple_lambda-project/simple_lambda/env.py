# -*- coding: utf-8 -*-

"""
Define the multi-environments setup for this project.
"""

import simple_lambda.vendor.aws_ops_alpha.api as aws_ops_alpha

from .runtime import runtime


class EnvEnum(aws_ops_alpha.BaseWorkloadEnvEnum):
    """
    Workload environment enumeration. Don't put devops environment name here.
    """

    sbx = aws_ops_alpha.SBX
    tst = aws_ops_alpha.TST
    prd = aws_ops_alpha.PRD


USER_ENV_NAME = aws_ops_alpha.USER_ENV_NAME


def detect_current_env() -> str:
    # ----------------------------------------------------------------------
    # you can uncomment this line to force to use certain env
    # from your local laptop to run application code, tests, ...
    # ----------------------------------------------------------------------
    # return EnvEnum.sbx.value
    return aws_ops_alpha.detect_current_env(runtime, EnvEnum)
