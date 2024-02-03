# -*- coding: utf-8 -*-

"""
AWS Lambda version and alias management helper functions.

Requirements::

    boto3

Optional Requirements::

    boto3-stubs[lambda]

Usage example::

    from aws_lambda_version_and_alias import (
        LATEST,
        list_versions_by_function,
        version_dct_to_version_int,
        get_last_published_version,
        publish_version,
        keep_n_most_recent_versions,
        deploy_alias,
        delete_alias,
    )

This module is originally from https://github.com/MacHu-GWU/fixa-project/blob/main/fixa/aws/aws_lambda_version_and_alias.py
"""

import typing as T

import botocore.exceptions

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_lambda import LambdaClient

__version__ = "0.1.1"

LATEST = "$LATEST"


def list_versions_by_function(
    lbd_client: "LambdaClient",
    func_name: str,
    max_items: int = 9999,
) -> T.List[dict]:
    """
    List all lambda function versions. Return a list of detail dict.
    """
    paginator = lbd_client.get_paginator("list_versions_by_function")
    response_iterator = paginator.paginate(
        FunctionName=func_name,
        PaginationConfig={
            "MaxItems": max_items,
            "PageSize": 50,
        },
    )
    versions = []
    for response in response_iterator:
        versions.extend(response.get("Versions", []))
    return versions


def version_dct_to_version_int(versions: T.List[dict]) -> T.List[int]:
    """
    Convert a list of lambda function version detail dict to a list of
    version number. The $LATEST version is not included.
    """
    int_versions = []
    for dct in versions:
        try:
            int_versions.append(int(dct["Version"]))
        except:
            pass
    return int_versions


def get_last_published_version(
    lbd_client: "LambdaClient",
    func_name: str,
    max_items: int = 9999,
) -> T.Optional[int]:
    """
    Get the last published version number. If there's no published version,
    return None.
    """
    versions = list_versions_by_function(lbd_client, func_name, max_items)
    int_versions = version_dct_to_version_int(versions)
    if int_versions:
        return max(int_versions)
    else:  # pragma: no cover
        return None


def publish_version(
    lbd_client: "LambdaClient",
    func_name: str,
) -> T.Tuple[bool, int]:
    """
    Publish a new version. The AWS official doc says that:
    Lambda doesn’t publish a version if the function’s configuration and
    code haven’t changed since the last version.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/publish_version.html

    :return: a tuple of two items, first item is a boolean flag to indicate
        that if a new version is created. the second item is the version id.
        if there's a new version is created, return the new version, otherwise,
        return the latest version number.
    """
    last_published_version = get_last_published_version(lbd_client, func_name)
    if last_published_version is None:  # pragma: no cover
        last_published_version = -1
    res = lbd_client.publish_version(FunctionName=func_name)
    published_version = int(res["Version"])
    if last_published_version == published_version:
        return False, published_version
    else:
        return True, published_version


def keep_n_most_recent_versions(
    lbd_client: "LambdaClient",
    func_name: str,
    n: int,
    max_items: int = 9999,
) -> T.List[int]:
    """
    Only keep the most recent n versions, delete the rest of published versions. If a version is associated with an alias, it will not be deleted.
    """
    versions = list_versions_by_function(lbd_client, func_name, max_items)
    int_versions = version_dct_to_version_int(versions)
    int_versions.sort()
    versions_to_delete = int_versions[:-n]
    for version in versions_to_delete:
        try:
            lbd_client.delete_function(
                FunctionName=f"{func_name}:{version}",
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceConflictException":
                pass
            else:  # pragma: no cover
                raise e
    return versions_to_delete


def deploy_alias(
    lbd_client: "LambdaClient",
    func_name: str,
    alias: str,
    description: T.Optional[str] = None,
    version1: T.Optional[T.Union[str, int]] = None,
    version2: T.Optional[T.Union[str, int]] = None,
    version2_percentage: T.Optional[float] = None,
) -> T.Tuple[bool, T.Optional[str]]:
    """
    Point the alias to the given version or split traffic between two versions.

    :param bsm: boto session manager object
    :param func_name: lambda function name
    :param alias: alias name
    :param description: description of the alias
    :param version1: the main version of the alias; if not specified, use $LATEST
    :param version2: the secondary version of the alias; if not specified, then
        the version1 will have 100% traffic; if specified, then version2_percentage
        also has to be specified.
    :param version2_percentage: if version2 is specified, then it has to be a
        value between 0.01 and 0.99.

    :return: a tuple of two items; first item is a boolean flag to indicate
        whether a creation or update is performed; second item is the alias
        revision id, if creation or update is not performed, then return None.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/get_alias.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/create_alias.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/update_alias.html
    """
    # find out the target version and resolve routing configuration
    if version1 is not None:
        version1 = str(version1)
    target_version = LATEST if version1 is None else version1
    if version2 is not None:
        version2 = str(version2)
        if not (0.01 <= version2_percentage <= 0.99):  # pragma: no cover
            raise ValueError("version2 percentage has to be between 0.01 and 0.99.")
        if target_version == LATEST:  # pragma: no cover
            raise ValueError(
                "$LATEST is not supported for an alias pointing to more than 1 version."
            )
        routing_config = dict(AdditionalVersionWeights={version2: version2_percentage})
    else:
        routing_config = {}

    create_or_update_alias_kwargs = dict(
        FunctionName=func_name,
        Name=alias,
        FunctionVersion=target_version,
    )
    if description:  # pragma: no cover
        create_or_update_alias_kwargs["Description"] = description

    create_or_update_alias_kwargs["RoutingConfig"] = routing_config

    try:
        # check if the alias exists
        response = lbd_client.get_alias(
            FunctionName=func_name,
            Name=alias,
        )
        # if exists, compare the current live version with the target version
        current_version = response["FunctionVersion"]
        current_routing_config = response.get("RoutingConfig", {})
        # update the target version
        if (current_version != target_version) or (
            current_routing_config != routing_config
        ):
            res = lbd_client.update_alias(**create_or_update_alias_kwargs)
            return True, res["RevisionId"]
        else:
            return False, None
    except botocore.exceptions.ClientError as e:
        # if not exists, create it
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            res = lbd_client.create_alias(**create_or_update_alias_kwargs)
            return True, res["RevisionId"]
        else:  # pragma: no cover
            raise e


def delete_alias(
    lbd_client: "LambdaClient",
    func_name: str,
    alias: str,
) -> dict:
    """
    The original API is already idempotent, so no need to check if the alias exists.
    """
    return lbd_client.delete_alias(
        FunctionName=func_name,
        Name=alias,
    )
