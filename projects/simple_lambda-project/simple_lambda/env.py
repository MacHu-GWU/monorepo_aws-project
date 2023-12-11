# -*- coding: utf-8 -*-

"""
Define the multi-environments setup for this project.
"""

import os

import config_patterns.api as config_patterns
import simple_lambda.vendor.aws_ops_alpha.api as aws_ops_alpha

from .runtime import runtime


class EnvEnum(config_patterns.multi_env_json.BaseEnvEnum):
    """
    Workload environment enumeration. Don't put devops environment name here.
    """
    sbx = aws_ops_alpha.SBX
    tst = aws_ops_alpha.TST
    # stg = aws_ops_alpha.STG
    prd = aws_ops_alpha.PRD


USER_ENV_NAME = aws_ops_alpha.USER_ENV_NAME


def detect_current_env() -> str:
    # ----------------------------------------------------------------------
    # you can uncomment this line to force to use certain env
    # from your local laptop to run application code, tests, ...
    # ----------------------------------------------------------------------
    # return EnvEnum.sbx.value
    # ----------------------------------------------------------------------
    # For local laptop, by default we use sbx environment
    # But you can use the "USER_ENV_NAME" environment variable to override it
    # ----------------------------------------------------------------------
    if runtime.is_local:
        if USER_ENV_NAME in os.environ:
            return os.environ[USER_ENV_NAME]
        return EnvEnum.sbx.value
    # ----------------------------------------------------------------------
    # For ci runtime, the job runtime should use the  "USER_ENV_NAME"
    # environment variable to identify the env name. If it is "devops"
    # we skip the env name validation
    # ----------------------------------------------------------------------
    elif runtime.is_ci:
        env_name = os.environ[USER_ENV_NAME]
        if env_name != aws_ops_alpha.DEVOPS:
            EnvEnum.ensure_is_valid_value(env_name)
        return env_name
    # ----------------------------------------------------------------------
    # For app runtime, it should use the  "USER_ENV_NAME" environment variable
    # to identify the env name. It should NEVER be "devops"
    # ----------------------------------------------------------------------
    else:
        env_name = os.environ[USER_ENV_NAME]
        EnvEnum.ensure_is_valid_value(env_name)
        return env_name
