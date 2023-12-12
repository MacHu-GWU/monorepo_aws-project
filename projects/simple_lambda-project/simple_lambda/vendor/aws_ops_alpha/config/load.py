# -*- coding: utf-8 -*-

"""
"""

import typing as T
import os
import json
from pathlib import Path

from config_patterns.api import multi_env_json
from ..vendor.jsonutils import json_loads

from ..constants import DEVOPS
from ..runtime import Runtime
from ..environment import BaseWorkloadEnvEnum, detect_current_env
from ..boto_ses import AbstractBotoSesFactory


def load_config(
    runtime: Runtime,
    env_enum: T.Union[BaseWorkloadEnvEnum, T.Type[BaseWorkloadEnvEnum]],
    config_class: T.Type[multi_env_json.BaseConfig],
    env_class: T.Type[multi_env_json.BaseEnv],
    path_config_json: T.Optional[Path] = None,
    path_config_secret_json: T.Optional[Path] = None,
    boto_ses_factory: T.Optional[AbstractBotoSesFactory] = None,
):
    """
    If you use the recommended multi-environments config management strategy,
    you can use this function to load the config object.

    1. on local, we consider the local json file as the source of truth. We read
        config data from ``path_config_json`` and ``path_config_secret_json`` files.
    2. on ci, we won't have the secret json file available, we read the non-sensitive
        config.json from git, figure out the aws ssm parameter name, then load config
        data from it.
    """
    if runtime.is_local:
        # ensure that the config-secret.json file exists
        # I recommend to put it at the ${HOME}/.projects/${project_name}/config-secret.json
        # if the user haven't created it yet, this code block will print helper
        # message and generate a sample config-secret.json file for the user.
        if not path_config_secret_json.exists():  # pragma: no cover
            print(
                f"create the initial {path_config_secret_json} "
                f"file for config data, please update it!"
            )
            path_config_secret_json.parent.mkdir(parents=True, exist_ok=True)
            initial_config_secret_data = {
                "_shared": {},
            }
            for env_name in env_enum:
                initial_config_secret_data[env_name] = {
                    "_comment": "make sure secret config match your config object definition"
                }
            config_secret_content = json.dumps(initial_config_secret_data, indent=4)
            path_config_secret_json.write_text(config_secret_content)

        # read non-sensitive config and sensitive config from local file system
        return config_class.read(
            env_class=env_class,
            env_enum_class=env_enum,
            path_config=f"{path_config_json}",
            path_secret_config=f"{path_config_secret_json}",
        )
    elif runtime.is_ci:
        # read non-sensitive config from local file system
        # and then figure out what is the parameter name
        config = config_class(
            data=json_loads(path_config_json.read_text()),
            secret_data=dict(),
            Env=env_class,
            EnvEnum=env_enum,
            version="not-applicable",
        )
        # read config from parameter store
        env_name = detect_current_env(runtime, env_enum)
        if env_name == DEVOPS:
            bsm = boto_ses_factory.bsm_devops
            parameter_name = config.parameter_name
        else:
            bsm = boto_ses_factory.get_env_bsm(env_name)
            parameter_name = config.env.parameter_name
        return config_class.read(
            env_class=env_class,
            env_enum_class=env_enum,
            bsm=bsm,
            parameter_name=parameter_name,
            parameter_with_encryption=True,
        )
    # app runtime
    else:
        # read the parameter name from environment variable
        parameter_name = os.environ["PARAMETER_NAME"]
        # read config from parameter store
        return config_class.read(
            env_class=env_class,
            env_enum_class=env_enum,
            bsm=boto_ses_factory.bsm,
            parameter_name=parameter_name,
            parameter_with_encryption=True,
        )
