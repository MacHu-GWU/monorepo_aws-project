# -*- coding: utf-8 -*-

import os
import json

from config_patterns.jsonutils import json_loads
import simple_lambda.vendor.aws_ops_alpha.api as aws_ops_alpha

from .._api import (
    paths,
    runtime,
    detect_current_env,
    boto_ses_factory,
    bsm,
)
from .define import EnvEnum, Env, Config

if runtime.is_local:
    # ensure that the config-secret.json file exists
    # it should be at the ${HOME}/.projects/simple_lambda/config-secret.json
    # this code block is only used to onboard first time user of this
    # project template. Once you know about how to handle the config-secret.json file,
    # you can delete this code block.
    if not paths.path_config_secret_json.exists():  # pragma: no cover
        paths.path_config_secret_json.parent.mkdir(parents=True, exist_ok=True)
        paths.path_config_secret_json.write_text(
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
        path_config=paths.path_config_json.abspath,
        path_secret_config=paths.path_config_secret_json.abspath,
    )
elif runtime.is_ci:
    # read non-sensitive config from local file system
    # and then figure out what is the parameter name
    config = Config(
        data=json_loads(paths.path_config_json.read_text()),
        secret_data=dict(),
        Env=Env,
        EnvEnum=EnvEnum,
        version="not-applicable",
    )
    # read config from parameter store
    # we consider the value in parameter store is the ground truth for production
    env_name = detect_current_env()
    if env_name == aws_ops_alpha.DEVOPS:
        bsm = boto_ses_factory.bsm_devops
    else:
        bsm = boto_ses_factory.get_env_bsm(env_name)
    print(f"{env_name = }")
    print(f"{bsm.aws_account_alias = }")
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
