# -*- coding: utf-8 -*-

import dataclasses
from functools import cached_property

import config_patterns.api as config_patterns
import simple_lambda.vendor.aws_ops_alpha.api as aws_ops_alpha
from ..._api import runtime, EnvEnum, detect_current_env

# You may have a long list of config field definition
# put them in different module and use Mixin class
from .app import AppMixin
from .lbd_deploy import LambdaDeployMixin
from .lbd_func import LambdaFunction, LambdaFunctionMixin


# inherit order matters, typically, you want to use your own Mixin class
# to override the default behavior, so you should inherit aws_ops_alpha.Env
# at the end. You can find more details about MRO at https://www.python.org/download/releases/2.3/mro/
@dataclasses.dataclass
class Env(
    AppMixin,
    LambdaDeployMixin,
    LambdaFunctionMixin,
    aws_ops_alpha.Env,
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


@dataclasses.dataclass
class Config(aws_ops_alpha.Config):
    @classmethod
    def get_current_env(cls) -> str:  # pragma: no cover
        return detect_current_env()

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
