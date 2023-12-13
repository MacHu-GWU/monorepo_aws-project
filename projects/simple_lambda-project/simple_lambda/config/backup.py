# -*- coding: utf-8 -*-

from .._version import __version__
from .._api import (
    paths,
    runtime,
    boto_ses_factory,
)
from .define.api import EnvNameEnum, Env, Config


def smart_backup():
    return Config.smart_backup(
        runtime=runtime,
        boto_ses_factory=boto_ses_factory,
        env_name_enum_class=EnvNameEnum,
        env_class=Env,
        version=__version__,
        path_config_json=paths.path_config_json,
        path_config_secret_json=paths.path_config_secret_json,
    )
