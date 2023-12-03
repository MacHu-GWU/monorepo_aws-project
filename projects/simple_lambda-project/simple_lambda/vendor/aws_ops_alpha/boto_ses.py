# -*- coding: utf-8 -*-

import typing as T
import abc
import dataclasses
from functools import cached_property

from boto_session_manager import BotoSesManager

from .constants import DEVOPS, SBX
from .config import Config
from .runtime import Runtime, runtime
from .env_var import (
    get_workload_aws_account_id_in_ci,
)


@dataclasses.dataclass
class BotoSes(abc.ABC):
    config: "Config" = dataclasses.field()
    runtime: "Runtime" = dataclasses.field()

    @abc.abstractmethod
    def get_env_role_name(self, env_name: str) -> str:
        """
        An abstract method to get the workload AWS account IAM role name for deployment.

        When configuring your cross account IAM role permission, you should
        consider how to parameterize the IAM role name using environment name.

        For example:

        - If you use different AWS accounts for different environments, then
            you can just return a constant string like ``"my_deployment_role"``.
        - If you use the same AWS account for different environments, isolating
            by naming convention, then you can use string like
            ``"my_{env_name}_deployment_role"``.
        """
        raise NotImplementedError

    def get_devops_bsm(self) -> "BotoSesManager":
        """
        Get the boto session manager for devops AWS account.
        """
        if self.runtime.is_local:
            return BotoSesManager(
                profile_name=self.config.env_aws_profile_mapper[DEVOPS]
            )
        elif self.runtime.is_ci:
            return BotoSesManager()
        else:  # pragma: no cover
            raise RuntimeError

    def get_env_bsm(
        self,
        env_name: str,
        role_session_name: T.Optional[str] = None,
        duration_seconds: int = 3600,
        region_name: T.Optional[str] = None,
        auto_refresh: bool = False,
    ) -> "BotoSesManager":
        """
        Get the boto session manager for workload AWS accounts by environment name.

        :param env_name: the environment name, for example, ``sbx``, ``tst``, ``prd``.
        :param role_session_name: the session name for the assumed role.
        :param duration_seconds: the duration in seconds for the assumed role.
        :param region_name: the region name for the assumed role, if not specified,
            then use the region name of the devops AWS account.
        :param auto_refresh: whether to auto refresh the assumed role.
        """
        if self.runtime.is_local:
            return BotoSesManager(
                profile_name=self.config.env_aws_profile_mapper[env_name],
            )
        elif self.runtime.is_ci:
            bsm_devops = self.get_devops_bsm()
            aws_account_id = get_workload_aws_account_id_in_ci(env_name)
            role_name = self.get_env_role_name(env_name)
            role_arn = f"arn:aws:iam::{aws_account_id}:role/{role_name}"
            if role_session_name is None:
                role_session_name = f"{env_name}_session"
            if region_name is None:
                region_name = bsm_devops.aws_region
            return bsm_devops.assume_role(
                role_arn=role_arn,
                role_session_name=role_session_name,
                duration_seconds=duration_seconds,
                region_name=region_name,
                auto_refresh=auto_refresh,
            )
        else:  # pragma: no cover
            raise RuntimeError

    def get_app_bsm(
        self,
        env_name: str = SBX,
    ) -> "BotoSesManager":
        """
        Get the boto session manager used for application for the workload AWS account.
        """
        if runtime.is_local:
            return BotoSesManager(
                profile_name=self.config.env_aws_profile_mapper[env_name]
            )
        elif runtime.is_ci:
            return BotoSesManager()
        else:
            return BotoSesManager()

    @cached_property
    def bsm_devops(self) -> "BotoSesManager":
        """
        The boto session manager for devops AWS account.
        Use this when building shared deployment code artifacts.
        """
        return self.get_devops_bsm()

    @cached_property
    def bsm_app(self) -> "BotoSesManager":
        """
        The boto session manager for workload AWS account.
        Use this in your application code most of the time.
        """
        return self.get_app_bsm()

    @cached_property
    def bsm(self) -> "BotoSesManager":
        """
        The shortcut to access the most commonly used boto session manager.
        Usually, it is the app boto session manager.
        """
        return self.bsm_app
