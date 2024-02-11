# -*- coding: utf-8 -*-

"""
Runtime refers to the specific computational environment in which your code
is executed. For example, running code on a local laptop, CI/CD build environments,
AWS EC2 instances, AWS Lambda functions, and more. Understanding the current runtime
is essential as it can impact how your code behaves.

For instance, when running your code on a local laptop, you might want to use
an AWS CLI named profile to access DevOps or workload AWS accounts. However,
in an application runtime like AWS Lambda, the default Boto session is typically
preconfigured for the current workload AWS account.

This Python module is designed to detect the current runtime information and
offers a set of ``is_xyz`` methods to assist you in crafting conditional logic
for performing different actions based on the runtime. Notably, many of these
methods employ the LAZY LOAD technique for efficiency.

While this module is an integral part of the
https://github.com/MacHu-GWU/aws_ops_alpha-project repository, it is also available
for standalone use.

Requirements: Python>=3.8

Dependencies::

    cached-property>=1.5.2; python_version < '3.8'
"""

import os
import sys
import enum
from functools import cached_property

try:
    from ..constants import EnvVarNameEnum

    USER_RUNTIME_NAME = EnvVarNameEnum.USER_RUNTIME_NAME.value
except ImportError:
    USER_RUNTIME_NAME = "USER_RUNTIME_NAME"


class RunTimeGroupEnum(str, enum.Enum):
    """
    Enumeration of common runtime groups in AWS projects.
    """

    local = "local"
    ci = "ci"
    app = "app"
    unknown = "unknown"


class RunTimeEnum(str, enum.Enum):
    """
    Enumeration of common runtime in AWS projects.
    """

    # local runtime group
    local = "local"
    aws_cloud9 = "aws_cloud9"
    # ci runtime group
    aws_codebuild = "aws_codebuild"
    github_action = "github_action"
    gitlab_ci = "gitlab_ci"
    bitbucket_pipeline = "bitbucket_pipeline"
    circleci = "circleci"
    jenkins = "jenkins"
    # app runtime group
    aws_lambda = "aws_lambda"
    aws_batch = "aws_batch"
    aws_glue = "aws_glue"
    aws_ec2 = "aws_ec2"
    aws_ecs = "aws_ecs"
    # special runtimes
    glue_container = "glue_container"
    unknown = "unknown"


runtime_emoji_mapper = {
    "local": "💻",
    "aws_cloud9": "💻",
    "aws_codebuild": "🔨",
    "github_action": "🔨",
    "gitlab_ci": "🔨",
    "bitbucket_pipeline": "🔨",
    "circleci": "🔨",
    "jenkins": "🔨",
    "aws_lambda": "🚀",
    "aws_batch": "🚀",
    "aws_glue": "🚀",
    "aws_ec2": "🚀",
    "aws_ecs": "🚀",
    "unknown": "❓",
}


def _check_user_env_var(expect: str) -> bool:
    return os.environ.get(USER_RUNTIME_NAME, "__unknown") == expect


class Runtime:
    """
    Detect the current runtime information by inspecting environment variables.

    The instance of this class is the entry point of all kinds of runtime related
    variables, methods.

    You can extend this class to add more runtime detection logic.
    """

    # --------------------------------------------------------------------------
    # detect if it is a specific runtime
    # --------------------------------------------------------------------------
    @cached_property
    def is_aws_codebuild(self) -> bool:
        """
        Reference:

        - https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html
        """
        if _check_user_env_var(RunTimeEnum.aws_codebuild.value):  # pragma: no cover
            return True
        return "CODEBUILD_BUILD_ID" in os.environ

    @cached_property
    def is_github_action(self) -> bool:
        """
        Reference:

        - https://docs.github.com/en/actions/learn-github-actions/variables
        """
        if _check_user_env_var(RunTimeEnum.github_action.value):  # pragma: no cover
            return True
        return "GITHUB_ACTION" in os.environ

    @cached_property
    def is_gitlab_ci(self) -> bool:
        """
        Reference:

        - https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
        """
        if _check_user_env_var(RunTimeEnum.gitlab_ci.value):  # pragma: no cover
            return True
        return "CI_PROJECT_ID" in os.environ

    @cached_property
    def is_bitbucket_pipeline(self) -> bool:
        """
        Reference:

        - https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
        """
        if _check_user_env_var(
            RunTimeEnum.bitbucket_pipeline.value
        ):  # pragma: no cover
            return True
        return "BITBUCKET_BUILD_NUMBER" in os.environ

    @cached_property
    def is_circleci(self) -> bool:
        """
        Reference:

        - https://circleci.com/docs/variables/
        """
        if _check_user_env_var(RunTimeEnum.circleci.value):  # pragma: no cover
            return True
        return "CIRCLECI" in os.environ

    @cached_property
    def is_jenkins(self) -> bool:
        """
        Reference:

        - https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-environment-variables
        """
        if _check_user_env_var(RunTimeEnum.jenkins.value):  # pragma: no cover
            return True
        return "BUILD_TAG" in os.environ and "EXECUTOR_NUMBER" in os.environ

    @cached_property
    def is_aws_lambda(self) -> bool:
        """
        Reference:

        - https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html
        """
        if _check_user_env_var(RunTimeEnum.aws_lambda.value):  # pragma: no cover
            return True
        return "AWS_LAMBDA_FUNCTION_NAME" in os.environ

    @cached_property
    def is_aws_batch(self) -> bool:
        """
        Reference:

        - https://docs.aws.amazon.com/batch/latest/userguide/job_env_vars.html
        """
        if _check_user_env_var(RunTimeEnum.aws_batch.value):  # pragma: no cover
            return True
        return "AWS_BATCH_JOB_ID" in os.environ

    @cached_property
    def is_aws_glue(self) -> bool:
        if _check_user_env_var(RunTimeEnum.aws_glue.value):  # pragma: no cover
            return True
        return "--JOB_RUN_ID" in sys.argv

    @cached_property
    def is_aws_cloud9(self) -> bool:
        """
        We use "C9" environment variable to detect AWS Cloud9 runtime.
        Note that this method may not be stable. But you could add the
        ``export C9=true`` to the ``~/.bashrc`` or ``~/.bash_profile``.

        Reference:

        - https://docs.aws.amazon.com/cloud9/latest/user-guide/env-vars.html
        """
        if _check_user_env_var(RunTimeEnum.aws_cloud9.value):  # pragma: no cover
            return True
        return "C9" in os.environ

    @cached_property
    def is_aws_ec2(self) -> bool:
        """
        There's no official way to detect if it is ec2 instance,
        you could set a custom environment variable for all your ec2 instances
        """
        if _check_user_env_var(RunTimeEnum.aws_ec2.value):  # pragma: no cover
            return True
        return "IS_AWS_EC2" in os.environ

    @cached_property
    def is_aws_ecs(self) -> bool:
        """
        There's no official way to detect if it is ecs task container,
        you could set a custom environment variable for all your ECS task.

        Reference:

        - https://docs.aws.amazon.com/AmazonECS/latest/userguide/taskdef-envfiles.html
        """
        if _check_user_env_var(RunTimeEnum.aws_ecs.value):  # pragma: no cover
            return True
        return "IS_AWS_ECS_TASK" in os.environ

    @cached_property
    def is_glue_container(self) -> bool:
        """
        There's no official way to detect if it is in a glue container.
        """
        if _check_user_env_var(RunTimeEnum.aws_ecs.value):  # pragma: no cover
            return True
        return os.environ.get("IS_GLUE_CONTAINER", "false") == "true"

    @cached_property
    def is_local(self) -> bool:
        """
        If it is not a CI or app runtimes, it is local.
        """
        if _check_user_env_var(RunTimeEnum.local.value):  # pragma: no cover
            return True

        # or is a short-circuit operator, the performance is good
        flag = (
            self.is_aws_codebuild
            or self.is_github_action
            or self.is_gitlab_ci
            or self.is_bitbucket_pipeline
            or self.is_circleci
            or self.is_jenkins
            or self.is_aws_lambda
            or self.is_aws_batch
            or self.is_aws_glue
            or self.is_aws_cloud9
            or self.is_aws_ec2
            or self.is_aws_ecs
            or self.is_glue_container
        )
        return not flag

    @cached_property
    def current_runtime(self) -> str:  # pragma: no cover
        """
        Return the human friendly name of the current runtime.
        """
        if os.environ.get(USER_RUNTIME_NAME, "__unknown") != "__unknown":
            return os.environ[USER_RUNTIME_NAME]

        if self.is_aws_codebuild:
            return RunTimeEnum.aws_codebuild.value
        if self.is_github_action:
            return RunTimeEnum.github_action.value
        if self.is_gitlab_ci:
            return RunTimeEnum.gitlab_ci.value
        if self.is_bitbucket_pipeline:
            return RunTimeEnum.bitbucket_pipeline.value
        if self.is_circleci:
            return RunTimeEnum.circleci.value
        if self.is_jenkins:
            return RunTimeEnum.jenkins.value
        if self.is_aws_lambda:
            return RunTimeEnum.aws_lambda.value
        if self.is_aws_batch:
            return RunTimeEnum.aws_batch.value
        if self.is_aws_glue:
            return RunTimeEnum.aws_glue.value
        if self.is_aws_cloud9:
            return RunTimeEnum.aws_cloud9.value
        if self.is_aws_ec2:
            return RunTimeEnum.aws_ec2.value
        if self.is_aws_ecs:
            return RunTimeEnum.aws_ecs.value
        if self.is_glue_container:
            return RunTimeEnum.glue_container.value
        if self.is_local:
            return RunTimeEnum.local.value
        return RunTimeEnum.unknown.value

    # --------------------------------------------------------------------------
    # detect if it is a specific runtime group
    # --------------------------------------------------------------------------
    @cached_property
    def is_local_runtime_group(self) -> bool:
        """
        Where developer has access to the local file system and operating system.
        """
        return self.is_local or self.is_aws_cloud9

    @cached_property
    def is_ci_runtime_group(self) -> bool:  # pragma: no cover
        """
        Where CI/CD automation code runs.
        """
        if (
            self.is_aws_codebuild
            or self.is_github_action
            or self.is_gitlab_ci
            or self.is_bitbucket_pipeline
            or self.is_circleci
            or self.is_jenkins
        ):
            return True
        else:
            return "CI" in os.environ

    @cached_property
    def is_app_runtime_group(self) -> bool:
        """
        Where application code runs.
        """
        return (
            self.is_aws_lambda
            or self.is_aws_batch
            or self.is_aws_glue
            or self.is_aws_cloud9
            or self.is_aws_ec2
            or self.is_aws_ecs
        )

    @cached_property
    def current_runtime_group(self) -> str:  # pragma: no cover
        """
        Return the human friendly name of the current runtime group.
        """
        if self.is_ci_runtime_group:
            return RunTimeGroupEnum.ci.value
        if self.is_app_runtime_group:
            return RunTimeGroupEnum.app.value
        if self.is_local_runtime_group:
            return RunTimeGroupEnum.local.value
        return RunTimeGroupEnum.unknown.value


# A singleton object that can be used in your concrete project.
runtime = Runtime()
