# -*- coding: utf-8 -*-

"""
Extend the ``config_patterns.multi_env_json`` module to add more AWS project
specific features.
"""

# standard library
import typing as T
import os
import json
import dataclasses
from pathlib import Path
from functools import cached_property

# third party library (include vendor)
import config_patterns.api as config_patterns
from ..vendor.jsonutils import json_loads

# modules from this project
from ..constants import CommonEnvNameEnum
from ..runtime.api import Runtime
from ..multi_env.api import BaseEnvNameEnum, detect_current_env
from ..boto_ses.api import AbstractBotoSesFactory

# modules from this submodule
from .app import AppMixin
from .name import NameMixin
from .deploy import DeployMixin

# type hint
if T.TYPE_CHECKING:  # pragma: no cover
    from s3pathlib import S3Path
    from boto_session_manager import BotoSesManager


@dataclasses.dataclass
class BaseEnv(
    config_patterns.multi_env_json.BaseEnv,
    AppMixin,
    NameMixin,
    DeployMixin,
):
    """
    Extend the ``config_patterns.multi_env_json.BaseEnv`` class to add more
    AWS project specific config fields and methods.

    Example::

        import typing as T
        import dataclasses

        @dataclasses.dataclass
        class Env(BaseEnv):
            username: T.Optional[str] = dataclasses.field(default=None)
            password: T.Optional[str] = dataclasses.field(default=None)
    """

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


T_BASE_ENV = T.TypeVar("T_BASE_ENV", bound=BaseEnv)


@dataclasses.dataclass
class BaseConfig(
    config_patterns.multi_env_json.BaseConfig[T_BASE_ENV],
    T.Generic[T_BASE_ENV],
):
    """
    Extend the ``config_patterns.multi_env_json.BaseConfig`` class to add more
    AWS project specific methods.

    Example::

        import typing as T
        import dataclasses

        @dataclasses.dataclass
        class Env(BaseEnv):
            username: T.Optional[str] = dataclasses.field(default=None)
            password: T.Optional[str] = dataclasses.field(default=None)

        @dataclasses.dataclass
        class Config(BaseConfig[Env]):
            @classmethod
            def get_current_env(cls) -> str:
                # your implementation here

            @property
            def sbx(self):
                return self.get_env("sbx")

            @property
            def tst(self):
                return self.get_env("tst")

            @property
            def stg(self):
                return self.get_env("stg")

            @property
            def prd(self):
                return self.get_env("prd")
    """

    @cached_property
    def devops(self):  # pragma: no cover
        return self.get_env(env_name=CommonEnvNameEnum.devops.value)

    @classmethod
    def smart_load(
        cls,
        runtime: Runtime,
        env_name_enum_class: T.Union[BaseEnvNameEnum, T.Type[BaseEnvNameEnum]],
        env_class: T.Type[T_BASE_ENV],
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

        :param runtime: the :class:`aws_ops_alpha.runtime.Runtime` object.
        :param env_name_enum_class: env name enumeration class, not the instance.
            a subclass of :class:`aws_ops_alpha.environment.BaseEnvNameEnum`.
        :param env_class: the :class:`aws_ops_alpha.config.define.main.BaseEnv` subclass.
        :param path_config_json: you need this parameter when loading data from local.
            it is where you store the non-sensitive config data json file.
        :param path_config_secret_json: you need this parameter when loading data from local.
            it is where you store the sensitive config data json file.
        :param boto_ses_factory: you need this parameter when loading data
            from AWS parameter store in CI.
        """
        if runtime.is_local_runtime_group:
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
                for env_name in env_name_enum_class:
                    initial_config_secret_data[env_name] = {
                        "make sure secret config match your config object definition": "...",
                    }
                config_secret_content = json.dumps(initial_config_secret_data, indent=4)
                path_config_secret_json.write_text(config_secret_content)

            # read non-sensitive config and sensitive config from local file system
            return cls.read(
                env_class=env_class,
                env_enum_class=env_name_enum_class,
                path_config=f"{path_config_json}",
                path_secret_config=f"{path_config_secret_json}",
            )
        elif runtime.is_ci_runtime_group:  # pragma: no cover
            # read non-sensitive config from local file system
            # and then figure out what is the parameter name
            config = cls(
                data=json_loads(path_config_json.read_text()),
                secret_data=dict(),
                Env=env_class,
                EnvEnum=env_name_enum_class,
                version="not-applicable",
            )
            # read config from parameter store
            env_name = detect_current_env(runtime, env_name_enum_class)
            if env_name == CommonEnvNameEnum.devops.value:
                bsm = boto_ses_factory.bsm_devops
                parameter_name = config.parameter_name
            else:
                bsm = boto_ses_factory.get_env_bsm(env_name)
                parameter_name = config.env.parameter_name
            return cls.read(
                env_class=env_class,
                env_enum_class=env_name_enum_class,
                bsm=bsm,
                parameter_name=parameter_name,
                parameter_with_encryption=True,
            )
        # app runtime
        else:  # pragma: no cover
            # read the parameter name from environment variable
            parameter_name = os.environ["PARAMETER_NAME"]
            # read config from parameter store
            return cls.read(
                env_class=env_class,
                env_enum_class=env_name_enum_class,
                bsm=boto_ses_factory.bsm,
                parameter_name=parameter_name,
                parameter_with_encryption=True,
            )

    @classmethod
    def smart_backup(
        cls,
        runtime: Runtime,
        bsm_devops: "BotoSesManager",
        env_name_enum_class: T.Union[BaseEnvNameEnum, T.Type[BaseEnvNameEnum]],
        env_class: T.Type[BaseEnv],
        version: str,
        path_config_json: T.Optional[Path] = None,
        path_config_secret_json: T.Optional[Path] = None,
        raise_error: bool = False,
    ) -> T.Tuple["S3Path", bool]:  # pragma: no cover
        """
        Create a backup of the current production config data in S3. The version
        is the project semantic version x.y.z. The version file is immutable.

        :param runtime: the :class:`aws_ops_alpha.runtime.Runtime` object.
        :param bsm_devops: boto session manager for devops account.
        :param env_name_enum_class: env name enumeration class, not the instance.
            a subclass of :class:`aws_ops_alpha.environment.BaseEnvNameEnum`.
        :param env_class: the :class:`aws_ops_alpha.config.define.main.BaseEnv` subclass.
        :param version: the project semantic version x.y.z
        :param path_config_json: you need this parameter when loading data from local.
            it is where you store the non-sensitive config data json file.
        :param path_config_secret_json: you need this parameter when loading data from local.
            it is where you store the sensitive config data json file.
        :param raise_error: if True, raises error when backup failed.
        """
        if runtime.is_local_runtime_group:
            config = cls.read(
                env_class=env_class,
                env_enum_class=env_name_enum_class,
                path_config=f"{path_config_json}",
                path_secret_config=f"{path_config_secret_json}",
            )
        elif runtime.is_ci_runtime_group:  # pragma: no cover
            # read non-sensitive config from local file system
            # and then figure out what is the parameter name
            config = cls(
                data=json_loads(path_config_json.read_text()),
                secret_data=dict(),
                Env=env_class,
                EnvEnum=env_name_enum_class,
                version="not-applicable",
            )
            config = cls.read(
                env_class=env_class,
                env_enum_class=env_name_enum_class,
                bsm=bsm_devops,
                parameter_name=config.parameter_name,
                parameter_with_encryption=True,
            )
        else:  # pragma: no cover
            raise RuntimeError

        config_data = {"data": config.data, "secret_data": config.secret_data}
        s3path = config.devops.s3dir_config.joinpath(f"{version}.json")
        if s3path.exists(bsm=bsm_devops):
            if raise_error:
                raise FileExistsError(
                    f"{version}.json already exists!"
                    f"You can not overwrite existing config snapshot backup!"
                    f"You should consider bump to a new version!"
                )
            else:
                return s3path, False
        tags = {
            "tech:note": (
                "this file is for production config data backup "
                "and it is immutable and do not overwrite and delete it"
            )
        }
        tags.update(config.env.devops_aws_tags)
        s3path.write_text(
            json.dumps(config_data, indent=4),
            bsm=bsm_devops,
            tags=tags,
        )
        return s3path, True


T_BASE_CONFIG = T.TypeVar("T_BASE_CONFIG", bound=BaseConfig)
