# -*- coding: utf-8 -*-

from .._api import (
    paths,
    runtime,
    boto_ses_factory,
)
from .define.api import EnvNameEnum, Env, Config


def smart_load():
    return Config.smart_load(
        runtime=runtime,
        env_name_enum_class=EnvNameEnum,
        env_class=Env,
        path_config_json=paths.path_config_json,
        path_config_secret_json=paths.path_config_secret_json,
        boto_ses_factory=boto_ses_factory,
    )


config = smart_load()
