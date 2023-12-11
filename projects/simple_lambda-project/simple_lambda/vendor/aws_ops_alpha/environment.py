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

import os

import config_patterns.api as config_patterns
from .vendor.emoji import Emoji

from .constants import DEVOPS, SBX, TST, STG, PRD, USER_ENV_NAME
from .runtime import Runtime


class EnvEnum(config_patterns.multi_env_json.BaseEnvEnum):
    """
    Environment name enumeration.
    """

    devops = DEVOPS
    sbx = SBX
    tst = TST
    stg = STG
    prd = PRD

    @property
    def emoji(self) -> str:
        """
        Return a emoji representation of the environment name.
        """
        return env_emoji_mapper[self.value]


env_emoji_mapper = {
    EnvEnum.devops.value: Emoji.devops,
    EnvEnum.sbx.value: Emoji.sbx,
    EnvEnum.tst.value: Emoji.tst,
    EnvEnum.stg.value: Emoji.stg,
    EnvEnum.prd.value: Emoji.prd,
}


def detect_current_env(runtime: Runtime) -> str:  # pragma: no cover
    """
    Smartly detect the current environment name.

    If it is a local runtime, by default, it is sandbox. User can override it
    by setting the environment name in the environment variable ``USER_ENV_NAME``.

    If it is a CI runtime or the application runtime, it uses the value
    of environment variable ``USER_ENV_NAME``.
    """
    if runtime.is_local:
        if USER_ENV_NAME in os.environ:
            return os.environ[USER_ENV_NAME]
        return EnvEnum.sbx.value
    elif runtime.is_ci:
        env_name = os.environ[USER_ENV_NAME]
        EnvEnum.ensure_is_valid_value(env_name)
        return env_name
    else:
        env_name = os.environ[USER_ENV_NAME]
        EnvEnum.ensure_is_valid_value(env_name)
        return env_name
