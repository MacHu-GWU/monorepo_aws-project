# -*- coding: utf-8 -*-

"""

"""

import typing as T
import abc
import dataclasses
from functools import cached_property

from boto_session_manager import BotoSesManager

from .constants import CommonEnvNameEnum
from .runtime import Runtime, runtime


@dataclasses.dataclass
class AbstractBotoSesFactory(abc.ABC):
    """
    Manages the creation of the
    `boto session manager (bsm) <https://pypi.org/project/boto-session-manager/>`_
    for multi-AWS-account, multi-environment deployment.

    For all bsm objects, it provides a factory method to create a new instance of the bsm object,
    and a cached_property to obtain the singleton object, reducing authentication overhead.

    An instance of this class serves as the central point for accessing
    different Boto sessions for AWS accounts in various environments.

    Note that THIS CLASS IS AN ABSTRACT CLASS, you should inherit from it and implement
    the following abstract methods before using it:

    - :meth:`AbstractBotoSesFactory.get_devops_bsm`
    - :meth:`AbstractBotoSesFactory.get_env_bsm`
    - :meth:`AbstractBotoSesFactory.get_app_bsm`
    - :meth:`AbstractBotoSesFactory.bsm_devops`
    - :meth:`AbstractBotoSesFactory.bsm_app`
    - :meth:`AbstractBotoSesFactory.bsm`

    Sample usage:

        >>> import dataclasses
        >>> from boto_session_manager import BotoSesManager
        >>> @dataclasses.dataclass
        ... class MyBotoSesFactory(AbstractBotoSesFactory):
        ...     def get_devops_bsm(self) -> BotoSesManager:
        ...         return BotoSesManager(profile_name="my_devops_profile")
        >>> boto_ses_factory = MyBotoSesFactory()
        >>> boto_ses_factory.bsm_devops.sts_client.get_caller_identity()
        {'UserId': '...', 'Account': '123456789012', 'Arn': '...'}
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

    @cached_property
    def bsm_devops(self) -> "BotoSesManager":
        """
        cached property of the :meth:`AbstractBotoSesFactory.get_devops_bsm`.
        """
        return self.get_devops_bsm()

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
        raise NotImplementedError


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
    default_app_env_name: str = dataclasses.field(default=CommonEnvNameEnum.sbx.value)

    @abc.abstractmethod
    def get_env_role_arn(self, env_name: str) -> str:
        """
        An abstract method to get the workload AWS account IAM role name for deployment.
        You have to subclass this class and implement this method.

        Usually, you only need this method in CI environment, because on local,
        you may just need to use AWS CLI named profile to assume the role.
        But in CI, you don't have AWS CLI named profile, you have to use the
        default role, which is the devops role to assume workload role.

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

    def get_current_env(self) -> str:
        """
        An abstract method to get the current environment name.
        """
        raise NotImplementedError

    def get_devops_bsm(self) -> "BotoSesManager":  # pragma: no cover
        """
        Get the boto session manager for devops AWS account.
        """
        if self.runtime.is_local:
            kwargs = dict(
                profile_name=self.env_to_profile_mapper[CommonEnvNameEnum.devops.value]
            )
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
    ) -> "BotoSesManager":  # pragma: no cover
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
            # ------------------------------------------------------------------
            # usually, the default boto session should be the devops bsm
            # but in CDK deploy shell script, we manually set the default
            # boto session as the workload bsm, in other words, the bsm_devops
            # is already the workload bsm. We need special handling here.
            # ------------------------------------------------------------------
            # bsm_devops.principal_arn could be either
            # arn:aws:iam::***:role/devops_role_name
            # arn:aws:sts::***:assumed-role/workload_role_name/session_name
            bsm_devops_role_name = bsm_devops.principal_arn.split("/", 1)[1]
            # role_arn should be
            # arn:aws:iam::***:role/workload_role_name
            bsm_workload_role_name = role_arn.split("/")[1]
            if bsm_devops_role_name.startswith(bsm_workload_role_name):
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

    def get_app_bsm(self) -> "BotoSesManager":  # pragma: no cover
        """
        Get the boto session manager for application code logic.
        """
        if runtime.is_local or self.runtime.is_aws_cloud9:
            return self.get_env_bsm(env_name=self.default_app_env_name)
        elif self.runtime.is_ci:
            return self.get_env_bsm(env_name=self.get_current_env())
        else:
            return BotoSesManager()

    @cached_property
    def bsm(self) -> "BotoSesManager":  # pragma: no cover
        """
        The shortcut to access the most commonly used boto session manager.
        Usually, it is for the application code.
        """
        return self.bsm_app
