# -*- coding: utf-8 -*-

"""
Define the multi-environments setup for this project.
"""

from .vendor.import_agent import aws_ops_alpha

from .runtime import runtime


class EnvNameEnum(aws_ops_alpha.BaseEnvNameEnum):
    """
    Environment enumeration. It has to have at least a devops, sbx and a prd
    environment.
    """

    devops = aws_ops_alpha.CommonEnvNameEnum.devops.value
    sbx = aws_ops_alpha.CommonEnvNameEnum.sbx.value
    tst = aws_ops_alpha.CommonEnvNameEnum.tst.value
    # stg = aws_ops_alpha.CommonEnvNameEnum.stg.value
    prd = aws_ops_alpha.CommonEnvNameEnum.prd.value


def detect_current_env() -> str:
    # ----------------------------------------------------------------------
    # you can uncomment this line to force to use certain env
    # from your local laptop to run application code, tests, ...
    # ----------------------------------------------------------------------
    # return EnvNameEnum.prd.value

    # use the aws_ops_alpha recommended setup
    return aws_ops_alpha.detect_current_env(runtime, EnvNameEnum)
