# -*- coding: utf-8 -*-

"""
Application related configurations.
"""

import typing as T
import dataclasses

from s3pathlib import S3Path

from ..constants import CommonEnvNameEnum, EnvVarNameEnum, AwsTagNameEnum

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import BaseEnv


@dataclasses.dataclass
class AppMixin:
    """
    Application related configurations.

    :param s3uri_data: an AWS project should always have a delegated s3 folder
        to store project data.
    """
    aws_account_id: T.Optional[str] = dataclasses.field(default=None)
    aws_region: T.Optional[str] = dataclasses.field(default=None)
    s3uri_data: T.Optional[str] = dataclasses.field(default=None)

    @property
    def s3dir_data(self) -> S3Path:
        """
        :class:`s3pathlib.S3Path` object of ``s3uri_data``
        """
        return S3Path.from_s3_uri(self.s3uri_data).to_dir()

    @property
    def s3dir_env_data(self: "BaseEnv") -> S3Path:
        """
        Environment specific s3 folder to store project data.
        """
        return self.s3dir_data.joinpath("envs", self.env_name).to_dir()

    @property
    def env_vars(self: "BaseEnv") -> T.Dict[str, str]:
        """
        Common environment variable for all computational resources in this environment.
        It is primarily for "self awareness" (detect who I am, which environment I am in).
        """
        return {
            EnvVarNameEnum.PARAMETER_NAME.value: self.parameter_name,
            EnvVarNameEnum.PROJECT_NAME.value: self.project_name,
            EnvVarNameEnum.ENV_NAME.value: self.env_name,
        }

    @property
    def devops_aws_tags(self: "BaseEnv") -> T.Dict[str, str]:
        """
        Common AWS resources tags for all resources in devops environment.
        """
        return {
            AwsTagNameEnum.tech_project_name.value: self.project_name,
            AwsTagNameEnum.tech_env_name.value: CommonEnvNameEnum.devops.value,
        }

    @property
    def workload_aws_tags(self: "BaseEnv") -> T.Dict[str, str]:
        """
        Common AWS resources tags for all resources in workload environment.
        """
        return {
            AwsTagNameEnum.tech_project_name.value: self.project_name,
            AwsTagNameEnum.tech_env_name.value: self.env_name,
        }
