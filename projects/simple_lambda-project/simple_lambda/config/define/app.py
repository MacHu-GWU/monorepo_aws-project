# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from s3pathlib import S3Path

from ..._version import __version__

if T.TYPE_CHECKING: # pragma: no cover
    from .main import Env


@dataclasses.dataclass
class AppMixin:
    username: T.Optional[str] = dataclasses.field(default=None)
    password: T.Optional[str] = dataclasses.field(default=None)

    s3uri_data: T.Optional[str] = dataclasses.field(default=None)
    s3bucket_docs: T.Optional[str] = dataclasses.field(default=None)

    @property
    def s3dir_data(self) -> S3Path:
        return S3Path.from_s3_uri(self.s3uri_data).to_dir()

    @property
    def s3dir_env_data(self: "Env") -> S3Path:
        return self.s3dir_data.joinpath("envs", self.env_name).to_dir()

    @property
    def s3dir_source(self: "Env") -> S3Path:
        return self.s3dir_env_data.joinpath("source").to_dir()

    @property
    def s3dir_target(self: "Env") -> S3Path:
        return self.s3dir_env_data.joinpath("target").to_dir()

    @property
    def env_vars(self: "Env") -> T.Dict[str, str]:
        """
        Common environment variable for all computational resources in this environment.
        It is primarily for "self awareness" (detect who I am, which environment I am in).
        """
        return {
            "PARAMETER_NAME": self.parameter_name,
            "PROJECT_NAME": self.project_name,
            "ENV_NAME": self.env_name,
            "PACKAGE_VERSION": __version__,
        }

    @property
    def aws_tags(self: "Env") -> T.Dict[str, str]:
        """
        Common AWS resources tags for all resources in this environment.
        """
        return {
            "tech:project_name": self.project_name,
            "tech:env_name": self.env_name,
            "tech:package_version": __version__,
        }
