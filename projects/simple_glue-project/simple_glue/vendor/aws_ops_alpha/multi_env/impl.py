# -*- coding: utf-8 -*-

"""
This module defines the multi-environments deployment strategy.

In ``aws_ops_alpha`` best practice, we have five environments:

- 🔧 devops: Serving as the foundation of the software development cycle, the
    DevOps environment is exclusively utilized for building code,
    conducting unit tests, and creating artifacts. The DevOps environment
    is not designated for application deployment.
- 📦 sbx-101, 102, 103: The sandbox serves as a temporary space for development
    or testing. It enables multiple engineers to concurrently work on
    different branches, ensuring that their parallel tasks do not interfere
    with each other. Each sandbox environment is uniquely identified by
    the naming convention 'sbx-${number}', where '${number}' can represent
    an agile user story, ticket ID, or GitHub issue ID. This setup facilitates
    ease of provisioning and destruction, making it an efficient,
    isolated workspace for developers and testers.
- 🧪 tst: The test environment is a durable and consistent setting dedicated
    to conducting integration and end-to-end testing. It is designed to be
    a comprehensive testing ground where various scenarios, including integration
    of different components and complete system functionality,
    are rigorously evaluated. Notably, this environment is crucial for executing
    high-risk tests, such as load testing and stress testing, that could potentially
    compromise system integrity. Its isolation from other environments ensures that
    such tests do not impact ongoing development or production activities.
    The test environment, therefore, acts as a critical buffer,
    safeguarding the overall system while allowing thorough and aggressive testing.
- 🎸 stg: Acting as the final step before deployment to production, the
    staging environment is meticulously set up to mirror production conditions,
    especially in terms of incoming workload. It is specifically designed for
    Quality Assurance (QA) teams to conduct extensive testing under
    realistic conditions. However, unlike production, outputs generated
    in the staging environment are not made visible to end users; instead,
    they are captured and retained for QA analysis. This environment is also
    instrumental in debugging production issues, offering a safe and accurate
    context for troubleshooting without affecting live operations. Thus,
    staging plays a pivotal role in ensuring software readiness
    and reliability before its release to end users.
- 🏭 prd: The production environment is the ultimate stage in the deployment pipeline,
    directly serving end-users. Following each successful deployment,
    it is a standard practice to create an immutable version of all artifacts
    used in that deployment. This immutable versioning enables quick and efficient
    rollbacks to any previous state, ensuring continuity and minimal disruption in service.
"""

import typing as T
import os
import string

import config_patterns.api as config_patterns
from ..vendor.emoji import Emoji

from ..constants import CommonEnvNameEnum, EnvVarNameEnum
from ..runtime.api import Runtime


_lowercase = set(string.ascii_lowercase)
_env_name_charset = set(string.ascii_lowercase + string.digits)


class EnvNameValidationError(ValueError):
    """
    Raise this error when the environment name is invalid.
    """


def validate_env_name(env_name: str):  # pragma: no cover
    """
    Validate the environment name. It has to be ``[a-z0-9]``, first letter
    has to be ``[a-z]``.
    """
    if env_name[0] not in _lowercase:
        raise EnvNameValidationError(
            f"{env_name!r} is an invalid env name, "
            f"first letter of env_name has to be a-z!"
        )
    if len(set(env_name).difference(_env_name_charset)):
        raise EnvNameValidationError(
            f"{env_name!r} is an invalid env name, " f"env_name can only has a-z, 0-9"
        )


class BaseEnvNameEnum(config_patterns.multi_env_json.BaseEnvEnum):
    """
    A base class for environment name enumerations.

    This class facilitates the referencing of environment names in your code,
    making it easier and more organized. Additionally, it provides several capabilities:

    1. Validation of environment names.
    2. Iteration over all available environment names.

    To define your own environment name enumerations class, you need to subclass
    this class. However, there are some restrictions:

    1. You cannot create a "devops" environment as it does not qualify as a workload environment.
    1. You must include at least a "devops", a "sbx" (sandbox) environment
        and a "prd" (production) environment.
    2. environment name has to be lower case, without

    A base class for environment name enumerations.

    It made easier to reference the environment name in the code. It also provides
    additional capabilities like:

    1. validate the environment name
    2. iterate over all environment names

    You have to subclass this class to define your own workload environments.
    There are some restriction:

    1. you cannot have "devops" environment, it is not workload environment.
    2. you have to have at least a "sbx" environment and a "prd" environment.
    """

    @classmethod
    def validate(cls):
        if (
            cls.is_valid_value(CommonEnvNameEnum.devops.value) is False
            or cls.is_valid_value(CommonEnvNameEnum.sbx.value) is False
            or cls.is_valid_value(CommonEnvNameEnum.prd.value) is False
        ):
            raise EnvNameValidationError(
                f"you have to define at least "
                f"a {CommonEnvNameEnum.devops.value!r}, "
                f"a {CommonEnvNameEnum.sbx.value!r}, "
                f"and a {CommonEnvNameEnum.prd.value!r} environment,"
                f"you only have {list(cls)}."
            )
        for env_name in cls:
            validate_env_name(env_name.value)

    @classmethod
    def _get_devops(cls):
        return cls.devops

    @classmethod
    def _get_sbx(cls):
        return cls.sbx

    @classmethod
    def _get_prd(cls):
        return cls.prd


env_emoji_mapper = {
    CommonEnvNameEnum.devops.value: Emoji.devops,
    CommonEnvNameEnum.sbx.value: Emoji.sbx,
    CommonEnvNameEnum.dev.value: Emoji.dev,
    CommonEnvNameEnum.tst.value: Emoji.tst,
    CommonEnvNameEnum.stg.value: Emoji.stg,
    CommonEnvNameEnum.qa.value: Emoji.qa,
    CommonEnvNameEnum.prd.value: Emoji.prd,
}


class EnvNameEnum(BaseEnvNameEnum):
    """
    aws_ops_alphas recommended multi-environments setup.
    """

    devops = CommonEnvNameEnum.devops.value
    sbx = CommonEnvNameEnum.sbx.value
    tst = CommonEnvNameEnum.tst.value
    stg = CommonEnvNameEnum.stg.value
    prd = CommonEnvNameEnum.prd.value

    @property
    def emoji(self) -> str:
        """
        Return an emoji representation of the environment name.
        """
        return env_emoji_mapper[self.value]


def detect_current_env(
    runtime: Runtime,
    env_name_enum_class: T.Union[BaseEnvNameEnum, T.Type[BaseEnvNameEnum]],
) -> str:  # pragma: no cover
    """
    Smartly detect the current environment name.

    1. If it is a local runtime, by default it is sandbox. User can override it
        by setting the environment name in the environment variable ``USER_ENV_NAME``.
    2. If it is a ci runtime or an app runtime, if prioritize to
        use ``USER_ENV_NAME`` environment variable, if it is not set,
        it will use the ``ENV_NAME`` environment variable.

    :param runtime: the :class:`aws_ops_alpha.runtime.Runtime` object, that
        is the entry point of all kinds of runtime related variables, methods..
    :param env_name_enum_class: a subclass of ``BaseEnvNameEnum``, note that
        this is NOT an instance, it is the enum class
    """
    # Validate the implementation of the enum.
    env_name_enum_class.validate()

    if runtime.is_local_runtime_group:
        if os.environ.get(EnvVarNameEnum.USER_ENV_NAME.value):
            return os.environ[EnvVarNameEnum.USER_ENV_NAME.value]
        return env_name_enum_class._get_sbx().value
    elif (
        runtime.is_ci_runtime_group
        or runtime.is_app_runtime_group
        or runtime.is_glue_container
    ):
        if os.environ.get(EnvVarNameEnum.USER_ENV_NAME.value):
            env_name = os.environ[EnvVarNameEnum.USER_ENV_NAME.value]
        else:
            env_name = os.environ[EnvVarNameEnum.ENV_NAME.value]
        env_name_enum_class.ensure_is_valid_value(env_name)
        return env_name
    else:  # pragma: no cover
        raise NotImplementedError
