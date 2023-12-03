# -*- coding: utf-8 -*-

import os
import json
from config_patterns.jsonutils import json_loads

from ..paths import path_config_json, path_config_secret_json
from ..runtime import runtime
from ..boto_ses import bsm

from .define import EnvEnum, Env, Config

if runtime.is_local:
    # ensure that the config-secret.json file exists
    # it should be at the ${HOME}/.projects/simple_lambda/config-secret.json
    # this code block is only used to onboard first time user of this
    # project template. Once you know about how to handle the config-secret.json file,
    # you can delete this code block.
    if not path_config_secret_json.exists():  # pragma: no cover
        path_config_secret_json.parent.mkdir(parents=True, exist_ok=True)
        path_config_secret_json.write_text(
            json.dumps(
                {
                    "_shared": {},
                    EnvEnum.sbx.value: {"password": f"{EnvEnum.sbx.value}.password"},
                    EnvEnum.tst.value: {"password": f"{EnvEnum.tst.value}.password"},
                    EnvEnum.prd.value: {"password": f"{EnvEnum.prd.value}.password"},
                },
                indent=4,
            )
        )

    # read non-sensitive config and sensitive config from local file system
    config = Config.read(
        env_class=Env,
        env_enum_class=EnvEnum,
        path_config=path_config_json.abspath,
        path_secret_config=path_config_secret_json.abspath,
    )
elif runtime.is_ci:
    # read non-sensitive config from local file system
    # and then figure out what is the parameter name
    config = Config(
        data=json_loads(path_config_json.read_text()),
        secret_data=dict(),
        Env=Env,
        EnvEnum=EnvEnum,
        version="not-applicable",
    )
    # read config from parameter store
    # we consider the value in parameter store is the ground truth for production
    config = Config.read(
        env_class=Env,
        env_enum_class=EnvEnum,
        bsm=bsm,
        parameter_name=config.parameter_name,
        parameter_with_encryption=True,
    )
elif runtime.is_aws_lambda:
    # read the parameter name from environment variable
    parameter_name = os.environ["PARAMETER_NAME"]
    # read config from parameter store
    config = Config.read(
        env_class=Env,
        env_enum_class=EnvEnum,
        bsm=bsm,
        parameter_name=parameter_name,
        parameter_with_encryption=True,
    )
else:
    raise NotImplementedError
