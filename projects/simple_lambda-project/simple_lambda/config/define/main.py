# -*- coding: utf-8 -*-

import dataclasses
import os

from config_patterns.patterns.multi_env_json.api import (
    BaseEnvEnum,
    BaseEnv,
    BaseConfig,
)

from ...runtime import runtime
from ...compat import cached_property


class EnvEnum(BaseEnvEnum):
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


# You may have a long list of config field definition
# put them in different module and use Mixin class
from .app import AppMixin
from .name import NameMixin
from .deploy import DeployMixin
from .lbd_deploy import LambdaDeployMixin
from .lbd_func import LambdaFunction, LambdaFunctionMixin


@dataclasses.dataclass
class Env(
    BaseEnv,
    AppMixin,
    NameMixin,
    DeployMixin,
    LambdaDeployMixin,
    LambdaFunctionMixin,
):
    @classmethod
    def from_dict(cls, data: dict):
        data["lambda_functions"] = {
            name: LambdaFunction(
                short_name=name,
                **dct,
            )
            for name, dct in data.get("lambda_functions", {}).items()
        }
        env = cls(**data)
        for lbd_func in env.lambda_functions.values():
            lbd_func.env = env
        return env


class Config(BaseConfig):
    @classmethod
    def get_current_env(cls) -> str: # pragma: no cover
        # you can uncomment this line to force to use certain env
        # from your local laptop to run application code, tests, ...
        # return EnvEnum.sbx.value
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

    @cached_property
    def sbx(self) -> Env: # pragma: no cover
        return self.get_env(env_name=EnvEnum.sbx)

    @cached_property
    def tst(self) -> Env: # pragma: no cover
        return self.get_env(env_name=EnvEnum.tst)

    @cached_property
    def prd(self) -> Env: # pragma: no cover
        return self.get_env(env_name=EnvEnum.prd)

    @cached_property
    def env(self) -> Env:
        return self.get_env(env_name=self.get_current_env())
