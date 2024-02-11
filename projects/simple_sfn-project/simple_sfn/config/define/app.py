# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from s3pathlib import S3Path

from ..._version import __version__

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import Env


@dataclasses.dataclass
class AppMixin:
    @property
    def s3dir_sfn_executions(self: "Env") -> S3Path:
        """
        A directory in S3 to store the state machine execution context data.
        """
        return self.s3dir_env_data.joinpath("sfn-executions").to_dir()

    @property
    def env_vars(self: "Env") -> T.Dict[str, str]:
        """
        Common environment variable for all computational resources in this environment.
        It is primarily for "self awareness" (detect who I am, which environment I am in).

        env vars include:

        - PARAMETER_NAME
        - PROJECT_NAME
        - ENV_NAME
        - PACKAGE_VERSION
        """
        env_vars = super().env_vars
        env_vars["PACKAGE_VERSION"] = __version__
        return env_vars

    @property
    def devops_aws_tags(self: "Env") -> T.Dict[str, str]:
        """
        Common AWS resources tags for all resources in devops environment.
        """
        tags = super().devops_aws_tags
        tags["tech:package_version"] = __version__
        return tags

    @property
    def workload_aws_tags(self: "Env") -> T.Dict[str, str]:
        """
        Common AWS resources tags for all resources in workload environment.
        """
        tags = super().workload_aws_tags
        tags["tech:package_version"] = __version__
        return tags
