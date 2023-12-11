# -*- coding: utf-8 -*-

import typing as T

if T.TYPE_CHECKING:
    import boto3

__version__ = "0.1.1"

def mask_aws_account_id(aws_account_id: str) -> str:
    """
    Example:

        >>> mask_aws_account_id("123456789012")
        '12*********12'
    """
    return aws_account_id[:2] + "*" * 8 + aws_account_id[-2:]


def mask_iam_principal_arn(arn: str) -> str:
    """
    Mask an IAM principal ARN.

    Example:

        >>> mask_iam_principal_arn("arn:aws:iam::123456789012:role/role-name")
        'arn:aws:iam::12*********12:role/role-name'
    """
    parts = arn.split(":")
    parts[4] = mask_aws_account_id(parts[4])
    masked_arn = ":".join(parts)
    return masked_arn


def get_account_info(
    boto_ses: "boto3.session.Session",
    masked_aws_account_id: bool = True,
) -> T.Tuple[str, str, str]:
    """
    Get the account ID, account alias and ARN of the given boto session.

    :param boto_ses: the boto3.session.Session object.
    :param masked_aws_account_id: whether to mask the account ID.

    :return: tuple of aws account_id, account_alias, arn of the given boto session
    """
    res = boto_ses.client("sts").get_caller_identity()
    account_id = res["Account"]
    arn = res["Arn"]
    res = boto_ses.client("iam").list_account_aliases()
    account_alias = res.get("AccountAliases", ["unknown-account-alias"])[0]
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
    """
    account_id, account_alias, arn = get_account_info(boto_ses, masked_aws_account_id)
    print(
        f"now we are on account {account_id} ({account_alias}), using principal {arn}"
    )
