# -*- coding: utf-8 -*-

import simple_lambda.vendor.aws_ops_alpha.api as aws_ops_alpha
from .._api import (
    paths,
    runtime,
    boto_ses_factory,
)
from .define.api import EnvNameEnum, Env, Config

config: Config = aws_ops_alpha.load_config(
    runtime=runtime,
    env_name_enum_class=EnvNameEnum,
    config_class=Config,
    env_class=Env,
    path_config_json=paths.path_config_json,
    path_config_secret_json=paths.path_config_secret_json,
    boto_ses_factory=boto_ses_factory,
)
