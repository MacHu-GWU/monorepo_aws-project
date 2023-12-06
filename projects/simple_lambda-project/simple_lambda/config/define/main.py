# -*- coding: utf-8 -*-

import dataclasses
import os

import config_patterns.api as config_patterns

from ...runtime import runtime
from ...compat import cached_property
from ...env import EnvEnum

# You may have a long list of config field definition
# put them in different module and use Mixin class
from .app import AppMixin
from .name import NameMixin
from .deploy import DeployMixin
from .lbd_deploy import LambdaDeployMixin
from .lbd_func import LambdaFunction, LambdaFunctionMixin


@dataclasses.dataclass
class Env(
    config_patterns.multi_env_json.BaseEnv,
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


class Config(config_patterns.multi_env_json.BaseConfig):
    @classmethod
    def get_current_env(cls) -> str:  # pragma: no cover
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
    def sbx(self) -> Env:  # pragma: no cover
        return self.get_env(env_name=EnvEnum.sbx)

    @cached_property
    def tst(self) -> Env:  # pragma: no cover
        return self.get_env(env_name=EnvEnum.tst)

    @cached_property
    def prd(self) -> Env:  # pragma: no cover
        return self.get_env(env_name=EnvEnum.prd)

    @cached_property
    def env(self) -> Env:
        return self.get_env(env_name=self.get_current_env())
