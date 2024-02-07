# -*- coding: utf-8 -*-

"""
Deployment related configs.
"""

import typing as T
import dataclasses

from s3pathlib import S3Path

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import BaseEnv


@dataclasses.dataclass
class DeployMixin:
    """
    Deployment related configs.

    :param s3uri_artifacts: where you want to store code artifacts, such as
        source code build, deployment package, cloudformation template,
        temp artifacts, etc ...
    :param s3uri_docs: where you want to store project documentation website.
        an AWS project should always have a delegated s3 folder
        to host the static documentation website.
    """

    s3uri_artifacts: T.Optional[str] = dataclasses.field(default=None)
    s3uri_docs: T.Optional[str] = dataclasses.field(default=None)

    @property
    def s3dir_artifacts(self: "BaseEnv") -> S3Path:  # pragma: no cover
        """
        Shared artifacts s3 dir for all environments.
        """
        return S3Path.from_s3_uri(self.s3uri_artifacts).to_dir()

    @property
    def s3dir_env_artifacts(self: "BaseEnv") -> S3Path:  # pragma: no cover
        """
        Env specific artifacts s3 dir.

        example: ``${s3dir_artifacts}/${env_name}/
        """
        return self.s3dir_artifacts.joinpath("envs", self.env_name).to_dir()

    @property
    def s3dir_tmp(self: "BaseEnv") -> S3Path:
        """
        example: ``${s3dir_artifacts}/tmp/``
        """
        return self.s3dir_artifacts.joinpath("tmp").to_dir()

    @property
    def s3dir_config(self: "BaseEnv") -> S3Path:
        """
        example: ``${s3dir_artifacts}/config/``
        """
        return self.s3dir_artifacts.joinpath("config").to_dir()

    @property
    def s3dir_docs(self: "BaseEnv") -> S3Path:  # pragma: no cover
        """
        Documentation website s3 directory.
        """
        return S3Path.from_s3_uri(self.s3uri_docs).to_dir()
