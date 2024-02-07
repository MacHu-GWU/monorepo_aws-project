# -*- coding: utf-8 -*-

"""
Manage environment variables, and provide utility method to consume them.
"""

import typing as T
import os

from .constants import CommonEnvNameEnum
from .vendor.env_var import temp_env_var, normalize_env_var_name

_ = temp_env_var
_ = normalize_env_var_name


def _get_key(
    env_name: str,
    keyword: str,
    suffix: T.Optional[str] = None,
) -> str:
    """
    Get devops AWS account ID in CI runtime. We assume that your store
    them in environment variables like ``DEVOPS_AWS_ACCOUNT_ID``, ``SBX_AWS_ACCOUNT_ID``.
    """
    CommonEnvNameEnum.ensure_is_valid_value(env_name)
    key = f"{env_name.upper()}_{keyword}"
    if suffix:
        if suffix.startswith("_") is False:
            suffix = f"_{suffix}"
        key = f"{key}{suffix}"
    return key


def get_environment_aws_account_id_in_ci(
    env_name: str,
    suffix: T.Optional[str] = None,
) -> str:  # pragma: no cover
    """
    Assuming that this code is running in a CI runtime, get the AWS environment
    specific account id. We assume that your store them in environment variables
    like ``DEVOPS_AWS_ACCOUNT_ID``, ``SBX_AWS_ACCOUNT_ID``, etc ...

    For example, you stored your DevOps aws account id in ``DEVOPS_AWS_ACCOUNT_ID``,
    then you can use ``get_environment_aws_account_id_in_ci("DEVOPS")`` to get the value.
    If you stored your aws account id in ``DEVOPS_AWS_ACCOUNT_ID_MY_ORG``, then
    you can use ``get_environment_aws_account_id_in_ci("DEVOPS", suffix="MY_ORG")``
    to get the value.
    """
    return os.environ[_get_key(env_name, "AWS_ACCOUNT_ID", suffix=suffix)]


def get_environment_iam_role_arn_in_dev_server(
    env_name: str,
    suffix: T.Optional[str] = None,
) -> str:  # pragma: no cover
    """
    Assuming that this code is running in a development server runtime, like
    AWS Cloud9, EC2 instance, get the AWS environment specific IAM role ARN
    to assume. We assume that your store them in environment variables like
    ``DEVOPS_IAM_ROLE_ARN``, ``SBX_IAM_ROLE_ARN``.

    Usage example is similar to :func:`get_environment_aws_account_id_in_ci`.
    """
    return os.environ[_get_key(env_name, "IAM_ROLE_ARN", suffix=suffix)]
