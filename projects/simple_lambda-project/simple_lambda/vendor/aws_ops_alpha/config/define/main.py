# -*- coding: utf-8 -*-

import dataclasses
from functools import cached_property

import config_patterns.api as config_patterns

# You may have a long list of config field definition
# put them in different module and use Mixin class
from .app import AppMixin
from .name import NameMixin
from .deploy import DeployMixin


@dataclasses.dataclass
class Env(
    config_patterns.multi_env_json.BaseEnv,
    AppMixin,
    NameMixin,
    DeployMixin,
):
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class Config(config_patterns.multi_env_json.BaseConfig):
    @classmethod
    def get_current_env(cls) -> str:  # pragma: no cover
        raise NotImplementedError("You must implement this method")

    @cached_property
    def env(self) -> Env:
        return self.get_env(env_name=self.get_current_env())
