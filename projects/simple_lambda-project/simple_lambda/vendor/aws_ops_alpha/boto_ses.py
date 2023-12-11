# -*- coding: utf-8 -*-

"""

"""

import typing as T
import abc
import dataclasses
from functools import cached_property

from boto_session_manager import BotoSesManager

from .constants import DEVOPS, SBX
from .runtime import Runtime, runtime
from .env_var import (
    get_workload_aws_account_id_in_ci,
)


@dataclasses.dataclass
class AbstractBotoSesFactory(abc.ABC):
    """
    Manages creation of boto session manager (bsm) for
    multi-aws-account, multi-environment deployment. For all bsm object,
    it provides a factory method to create a new instance of the bsm object,
    and a cached_property to get the singleton object to reduce
    authentication overhead.

    The instance of this class is the central place to access different boto session
    for different environments' AWS account.
    """

    @abc.abstractmethod
    def get_devops_bsm(self) -> "BotoSesManager":
        """
        Get the boto session manager for devops AWS account.

        This bsm is used in devops automation or CI/CD pipeline for upload artifacts.
        It SHOULD NOT be used by the application code.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_env_bsm(self, env_name: str) -> "BotoSesManager":
        """
        Get the boto session manager for workload AWS account.

        This bsm is used to in devops automation or CI/CD pipeline for app deployment.
        Developers can also use this method to explicitly switch to the AWS account
        of a specific environment.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_app_bsm(self) -> "BotoSesManager":
        """
        Get the boto session manager for application code logic.
        """
        raise NotImplementedError

    @abc.abstractmethod
    @cached_property
    def bsm_devops(self) -> "BotoSesManager":
        """
        cached property of the :meth:`AbstractBotoSesFactory.get_devops_bsm`.
        """
        return self.get_devops_bsm()

    @abc.abstractmethod
    @cached_property
    def bsm_app(self) -> "BotoSesManager":
        """
        cached property of the :meth:`AbstractBotoSesFactory.get_app_bsm`.
        """
        return self.get_app_bsm()

    @abc.abstractmethod
    @cached_property
    def bsm(self) -> "BotoSesManager":
        """
        The shortcut to access the most commonly used boto session manager.
        Usually, it is for the application code.
        """
        return self.bsm_app


@dataclasses.dataclass
class AlphaBotoSesFactory(AbstractBotoSesFactory):
    """
    Manages creation of boto session manager for multi-aws-account, multi-environment
    deployment.

    The instance of this class is the central place to access different boto session
    for different environments' AWS account.

    Using this class, you agree to the following assumptions:

    1. You use AWS CLI named profile to access devops and workload AWS accounts.
        on your local laptop. You should provide the ``env_to_profile_mapper``
        attribute to map the environment name to the AWS CLI named profile name.
        make sure your AWS CLI named profile also defines the region name.
    2. You use IAM role for devops and assumed IAM role for workload AWS accounts
        on CI/CD or AWS Cloud 9 runtime. The default IAM principal should be
        on the devops AWS account, and the assumed IAM role should be on the
        workload AWS accounts. The CI/CD or AWS Cloud 9 runtime should have a
        mechanism to find the workload IAM role arn. For example, you can
        store them in environment variables.
    3. In your application runtime, such as AWS EC2, Lambda, the default
        IAM principal is already on the workload AWS account.

    :param env_to_profile_mapper: a dictionary to map the environment name to the
        AWS CLI named profile name. Normally, it should have the following keys:
        ``devops``, ``sbx``, ``tst``, ``stg``, ``prd``.
    :param aws_region: if specified, use this region name to create the boto session.
    """

    runtime: "Runtime" = dataclasses.field()
    env_to_profile_mapper: T.Dict[str, str] = dataclasses.field(default_factory=dict)
    aws_region: T.Optional[str] = dataclasses.field(default=None)
    default_app_env_name: str = dataclasses.field(default=SBX)

    @abc.abstractmethod
    def get_env_role_arn(self, env_name: str) -> str:
        """
        An abstract method to get the workload AWS account IAM role name for deployment.
        You have to subclass this class and implement this method.

        I recommend you to use environment variable to store the IAM role name.
        Let say you have three environments, sbx, tst, prd. Then you can create
        three environment variables, SBX_AWS_ACCOUNT_ID, TST_AWS_ACCOUNT_ID,
        PRD_AWS_ACCOUNT_ID. And use the following naming convention for workload
        IAM role arn: ``arn:aws:iam::{AWS_ACCOUNT_ID}:role/{ENV_NAME}_deployment_role``.
        In this way, the implementation of this method should be:

            >>> import os
            >>> def get_env_role_arn(self, env_name: str) -> str:
            ...     aws_account_id = os.environ[f"{env_name.upper()}_AWS_ACCOUNT_ID"]
            ...     return f"arn:aws:iam::{aws_account_id}:role/{env_name}_deployment_role"
        """
        raise NotImplementedError

    def get_devops_bsm(self) -> "BotoSesManager":
        """
        Get the boto session manager for devops AWS account.
        """
        if self.runtime.is_local:
            kwargs = dict(profile_name=self.env_to_profile_mapper[DEVOPS])
            if self.aws_region:
                kwargs["region_name"] = self.aws_region
            return BotoSesManager(**kwargs)
        elif self.runtime.is_ci or self.runtime.is_aws_cloud9:
            if self.aws_region:
                return BotoSesManager(region_name=self.aws_region)
            else:
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
        Get the boto session manager for workload AWS account.

        This bsm is used to in devops automation or CI/CD pipeline for app deployment.
        Developers can also use this method to explicitly switch to the AWS account
        of a specific environment.

        :param env_name: the environment name, for example, ``sbx``, ``tst``, ``prd``.
        :param role_session_name: the session name for the assumed role.
        :param duration_seconds: the duration in seconds for the assumed role.
        :param region_name: the region name for the assumed role, if not specified,
            then use the region name of the devops AWS account.
        :param auto_refresh: whether to auto refresh the assumed role.
        """
        if self.runtime.is_local:
            kwargs = dict(profile_name=self.env_to_profile_mapper[env_name])
            if self.aws_region:
                kwargs["region_name"] = self.aws_region
            return BotoSesManager(**kwargs)
        elif self.runtime.is_ci or self.runtime.is_aws_cloud9:
            bsm_devops = self.get_devops_bsm()
            role_arn = self.get_env_role_arn(env_name)
            print(bsm_devops.principal_arn)
            print(role_arn)
            # usually, the default boto session should be the devops bsm
            # but in CDK deploy shell script, we manually set the default
            # boto session as the workload bsm, in other words, the bsm_devops
            # is already the workload bsm. We need special handling here.
            if bsm_devops.principal_arn.startswith(role_arn):
                return bsm_devops

            if role_session_name is None:
                role_session_name = f"{env_name}_session"
            if region_name is None:
                if self.aws_region is None:
                    region_name = bsm_devops.aws_region
                else:
                    region_name = self.aws_region

            return bsm_devops.assume_role(
                role_arn=role_arn,
                role_session_name=role_session_name,
                duration_seconds=duration_seconds,
                region_name=region_name,
                auto_refresh=auto_refresh,
            )
        else:  # pragma: no cover
            raise RuntimeError

    def get_app_bsm(self) -> "BotoSesManager":
        """
        Get the boto session manager for application code logic.
        """
        if runtime.is_local:
            return self.get_env_bsm(env_name=self.default_app_env_name)
        elif self.runtime.is_ci or self.runtime.is_aws_cloud9:
            return self.get_env_bsm(env_name=self.default_app_env_name)
        else:
            return BotoSesManager()

    @cached_property
    def bsm_devops(self) -> "BotoSesManager":
        """
        cached property of the :meth:`AlphaBotoSesFactory.get_devops_bsm`.
        """
        return self.get_devops_bsm()

    @cached_property
    def bsm_app(self) -> "BotoSesManager":
        """
        cached property of the :meth:`AlphaBotoSesFactory.get_app_bsm`.
        """
        return self.get_app_bsm()

    @cached_property
    def bsm(self) -> "BotoSesManager":
        """
        The shortcut to access the most commonly used boto session manager.
        Usually, it is for the application code.
        """
        return self.bsm_app
