# -*- coding: utf-8 -*-

import os
import aws_ops_alpha.api as aws_ops_alpha
import config_patterns.api as config_patterns

from .runtime import runtime


class EnvEnum(config_patterns.multi_env_json.BaseEnvEnum):
    devops = aws_ops_alpha.constants.DEVOPS
    sbx = aws_ops_alpha.constants.SBX
    tst = aws_ops_alpha.constants.TST
    prd = aws_ops_alpha.constants.PRD


USER_ENV_NAME = aws_ops_alpha.constants.USER_ENV_NAME


def detect_current_env() -> str:
    # ----------------------------------------------------------------------
    # you can uncomment this line to force to use certain env
    # from your local laptop to run application code, tests, ...
    # ----------------------------------------------------------------------
    if runtime.is_local:
        if USER_ENV_NAME in os.environ:
            return os.environ[USER_ENV_NAME]
        return EnvEnum.sbx.value
    elif runtime.is_ci:
        env_name = os.environ[USER_ENV_NAME]
        EnvEnum.ensure_is_valid_value(env_name)
        return env_name
    else:
        env_name = os.environ[USER_ENV_NAME]
        EnvEnum.ensure_is_valid_value(env_name)
        return env_name
