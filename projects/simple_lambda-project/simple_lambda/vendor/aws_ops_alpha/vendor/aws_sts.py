# -*- coding: utf-8 -*-

"""
AWS Secure Token Service enhancement.

Usage::

    from fixa.aws.aws_sts import (
        mask_user_id,
        mask_aws_account_id,
        mask_iam_principal_arn,
        get_caller_identity,
        get_account_alias,
        get_account_info,
        print_account_info,
    )
"""

import typing as T

if T.TYPE_CHECKING:  # pragma: no cover
    import boto3
    from mypy_boto3_sts import STSClient
    from mypy_boto3_iam import IamClient

__version__ = "0.2.1"


def mask_user_id(user_id: str) -> str:
    """
    Example:

        >>> mask_user_id("A1B2C3D4GABCDEFGHIJKL")
        'A1B2***IJKL'

    .. versionadded:: 0.2.1
    """
    return user_id[:4] + "*" * 3 + user_id[-4:]


def mask_aws_account_id(aws_account_id: str) -> str:
    """
    Example:

        >>> mask_aws_account_id("123456789012")
        '12*********12'

    .. versionadded:: 0.1.1
    """
    return aws_account_id[:2] + "*" * 8 + aws_account_id[-2:]


def mask_iam_principal_arn(arn: str) -> str:
    """
    Mask an IAM principal ARN.

    Example:

        >>> mask_iam_principal_arn("arn:aws:iam::123456789012:role/role-name")
        'arn:aws:iam::12*********12:role/role-name'

    .. versionadded:: 0.1.1
    """
    parts = arn.split(":")
    parts[4] = mask_aws_account_id(parts[4])
    masked_arn = ":".join(parts)
    return masked_arn


def get_caller_identity(
    sts_client: "STSClient",
    masked: bool = False,
) -> T.Tuple[str, str, str]:
    """
    A wrapper of boto3.client("sts").get_caller_identity(). But it can mask the
    returned value.

    .. versionadded:: 0.2.1
    """
    res = sts_client.get_caller_identity()
    user_id = res["UserId"]
    account_id = res["Account"]
    arn = res["Arn"]
    if masked:
        user_id = mask_user_id(user_id)
        account_id = mask_aws_account_id(account_id)
        arn = mask_iam_principal_arn(arn)
    return user_id, account_id, arn


def get_account_alias(
    iam_client: "IamClient",
) -> T.Optional[str]:
    """
    Get AWS Account alias. If no alias is set, return None.

    Reference:

    - https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html

    .. versionadded:: 0.2.1
    """
    res = iam_client.list_account_aliases()
    return res.get("AccountAliases", [None])[0]


def get_account_info(
    boto_ses: "boto3.session.Session",
    masked_aws_account_id: bool = False,
) -> T.Tuple[str, str, str]:
    """
    Get the account ID, account alias and ARN of the given boto session.

    :param boto_ses: the boto3.session.Session object.
    :param masked_aws_account_id: whether to mask the account ID.

    :return: tuple of aws account_id, account_alias, arn of the given boto session

    .. versionadded:: 0.1.1
    """
    user_id, account_id, arn = get_caller_identity(
        boto_ses.client("sts"), masked_aws_account_id
    )
    account_alias = get_account_alias(boto_ses.client("iam"))
    if masked_aws_account_id:
        account_id = mask_aws_account_id(account_id)
        arn = mask_iam_principal_arn(arn)
    return account_id, account_alias, arn


def print_account_info(
    boto_ses: "boto3.session.Session",
    masked_aws_account_id: bool = True,
):
    """
    Display the account ID, account alias and ARN of the given boto session.

    :param boto_ses: the boto3.session.Session object.
    :param masked_aws_account_id: whether to mask the account ID.

    .. versionadded:: 0.1.1
    """
    account_id, account_alias, arn = get_account_info(boto_ses, masked_aws_account_id)
    print(
        f"now we are on account {account_id} ({account_alias}), using principal {arn}"
    )
