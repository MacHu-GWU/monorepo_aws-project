# -*- coding: utf-8 -*-

import os

import aws_ops_alpha.api as aws_ops_alpha
import config_patterns.api as config_patterns

from .runtime import runtime


class EnvEnum(config_patterns.multi_env_json.BaseEnvEnum):
    """
    In this project, we have three environment:

    - sbx: represent the developer's local laptop, and the sandbox environment
        the change you made on your local laptop can be applied to sandbox.
    - tst: a long living integration test environment. before releasing to
        production, the app has to be deployed to test environment for QA.
    - prd: the production environment. can only be deployed from release branch.
    """

    sbx = "sbx"
    tst = "tst"
    prd = "prd"

    @property
    def emoji(self) -> str:
        return env_emoji_mapper[self.value]


env_emoji_mapper = {
    EnvEnum.sbx.value: aws_ops_alpha.Emoji.sbx,
    EnvEnum.tst.value: aws_ops_alpha.Emoji.tst,
    EnvEnum.prd.value: aws_ops_alpha.Emoji.prd,
}


def get_current_env() -> str:  # pragma: no cover
    # --------------------------------------------------------------------------
    # you can uncomment this line to force to use certain env
    # from your local laptop to run application code, tests, ...
    # --------------------------------------------------------------------------
    # return EnvEnum.sbx.value

    # --------------------------------------------------------------------------
    # Detect the current environment name
    # --------------------------------------------------------------------------
    if runtime.is_local:
        if "USER_ENV_NAME" in os.environ:
            return os.environ["USER_ENV_NAME"]
        return EnvEnum.sbx.value
    elif runtime.is_ci:
        env_name = os.environ["USER_ENV_NAME"]
        EnvEnum.ensure_is_valid_value(env_name)
        return env_name
    elif runtime.is_aws_lambda:
        env_name = os.environ["ENV_NAME"]
        EnvEnum.ensure_is_valid_value(env_name)
        return env_name
