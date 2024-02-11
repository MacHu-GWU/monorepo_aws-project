# -*- coding: utf-8 -*-

"""
AWS StepFunction version and alias management helper functions.

Requirements::

    boto3

Optional Requirements::

    boto3-stubs[lambda]

Usage example::

    from aws_stepfunction_version_and_alias import (
        __version__,
        describe_state_machine,
        list_state_machine_versions,
        extract_version_from_arn,
        version_dct_to_version_int,
        get_last_published_version,
        publish_version,
        keep_n_most_recent_versions,
        describe_state_machine_alias,
        list_state_machine_aliases,
        extract_alias_from_arn,
        alias_dct_to_alias_name,
        to_route_config_dict_view,
        to_route_config_list_view,
        get_alias_routing_config,
        deploy_alias,
        delete_alias,
    )

This module is originally from https://github.com/MacHu-GWU/fixa-project/blob/main/fixa/aws/aws_stepfunctions_version_and_alias.py
"""

import typing as T
import time

import botocore.exceptions

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_stepfunctions import SFNClient


__version__ = "0.1.1"


def describe_state_machine(
    sfn_client: "SFNClient",
    state_machine_arn: str,
) -> T.Optional[dict]:
    """
    Describe a state machine. Return None if the state machine doesn't exist.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/describe_state_machine.html
    """
    try:
        return sfn_client.describe_state_machine(
            stateMachineArn=state_machine_arn,
        )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "StateMachineDoesNotExist":
            return None
        else:  # pragma: no cover
            raise e


def list_state_machine_versions(
    sfn_client: "SFNClient",
    state_machine_arn: str,
    max_results: int = 1000,
) -> T.List[dict]:
    """
    List all state machine versions. Return a list of detail dict.

    The AWS Official doc says that: The results are sorted in descending order
    of the version creation time.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/list_state_machine_versions.html

    :param sfn_client: ``boto3.client("stepfunctions")`` object.
    """
    versions = list()

    next_token = None
    kwargs = dict(
        stateMachineArn=state_machine_arn,
        maxResults=max_results,
    )
    while True:
        if next_token:
            kwargs["nextToken"] = next_token
        response = sfn_client.list_state_machine_versions(**kwargs)
        versions.extend(response.get("stateMachineVersions", []))
        next_token = response.get("nextToken")
        if bool(next_token) is False:
            break
    return versions


def extract_version_from_arn(arn: str) -> int:
    """
    Example::

        >>> extract_version_from_arn("arn:aws:states:us-east-1:123456789012:stateMachine:HelloWorld:1")
        1
    """
    return int(arn.split(":")[-1])


def version_dct_to_version_int(versions: T.List[dict]) -> T.List[int]:
    """
    Convert a list of state machine version detail dict to a list of
    version number.
    """
    return [extract_version_from_arn(dct["stateMachineVersionArn"]) for dct in versions]


def get_last_published_version(
    sfn_client: "SFNClient",
    state_machine_arn: str,
    max_results: int = 1,
) -> T.Optional[int]:
    """
    Get the last published version number. If there's no published version,
    return None.

    :param sfn_client: ``boto3.client("stepfunctions")`` object.
    """
    versions = list_state_machine_versions(
        sfn_client,
        state_machine_arn,
        max_results,
    )
    int_versions = version_dct_to_version_int(versions)
    if int_versions:
        return max(int_versions)
    else:  # pragma: no cover
        return None


def publish_version(
    sfn_client: "SFNClient",
    state_machine_arn: str,
    description: T.Optional[str] = None,
) -> T.Tuple[bool, int]:
    """
    Publish a new version. The AWS official doc says that:
    StepFunctions doesn’t publish a version if the state machine’s configuration
    and definition haven’t changed since the last version.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/publish_state_machine_version.html

    :param sfn_client: ``boto3.client("stepfunctions")`` object.

    :return: a tuple of two items, first item is a boolean flag to indicate
        that if a new version is created. the second item is the version id.
        if there's a new version is created, return the new version, otherwise,
        return the latest version number.
    """
    last_published_version = get_last_published_version(sfn_client, state_machine_arn)
    if last_published_version is None:  # pragma: no cover
        last_published_version = -1
    kwargs = dict(stateMachineArn=state_machine_arn)
    if description is not None:
        kwargs["description"] = description

    res = sfn_client.publish_state_machine_version(**kwargs)
    published_version = extract_version_from_arn(res["stateMachineVersionArn"])
    if last_published_version == published_version:
        return False, published_version
    else:
        return True, published_version


def keep_n_most_recent_versions(
    sfn_client: "SFNClient",
    state_machine_arn: str,
    n: int,
    max_items: int = 1000,
    skip_in_use_version: bool = True,
) -> T.List[int]:
    """
    Only keep the most recent n versions, delete the rest of published versions.
    If a version is associated with an alias, it will not be deleted.

    :param sfn_client: ``boto3.client("stepfunctions")`` object.
    :param n: number of latest version to keep
    :param max_items: max number of versions to list in one request.
    :param skip_in_use_version: if True, skip the version that is in use.
        if False, raise an exception if the version is in use.
    """
    versions = list_state_machine_versions(
        sfn_client,
        state_machine_arn,
        max_items,
    )
    int_versions = version_dct_to_version_int(versions)
    int_versions.sort()
    versions_to_delete = int_versions[:-n]
    for version in versions_to_delete:
        try:
            sfn_client.delete_state_machine_version(
                stateMachineVersionArn=f"{state_machine_arn}:{version}",
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceConflictException":
                pass
            elif e.response["Error"]["Code"] == "ConflictException":
                if skip_in_use_version:
                    continue
                else:  # pragma: no cover
                    raise e
            else:  # pragma: no cover
                raise e
    return versions_to_delete


# ------------------------------------------------------------------------------
# Alias
# ------------------------------------------------------------------------------
def describe_state_machine_alias(
    sfn_client: "SFNClient",
    state_machine_alias_arn: str,
) -> T.Optional[dict]:
    """
    Describe a state machine alias. Return None if the alias doesn't exist.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/describe_state_machine_alias.html

    :param sfn_client: ``boto3.client("stepfunctions")`` object.
    """
    try:
        return sfn_client.describe_state_machine_alias(
            stateMachineAliasArn=state_machine_alias_arn,
        )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFound":
            return None
        else:  # pragma: no cover
            raise e


def list_state_machine_aliases(
    sfn_client: "SFNClient",
    state_machine_arn: str,
    max_results: int = 1000,
) -> T.List[dict]:
    """
    List all state machine versions. Return a list of detail dict.

    The AWS Official doc says that: The results are sorted in descending order
    of the version creation time.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/list_state_machine_aliases.html

    :param sfn_client: ``boto3.client("stepfunctions")`` object.
    """
    alias_list = list()
    next_token = None
    kwargs = dict(
        stateMachineArn=state_machine_arn,
        maxResults=max_results,
    )
    while True:
        if next_token:
            kwargs["nextToken"] = next_token
        response = sfn_client.list_state_machine_aliases(**kwargs)
        alias_list.extend(response.get("stateMachineAliases", []))
        next_token = response.get("nextToken")
        if bool(next_token) is False:
            break
    return alias_list


def extract_alias_from_arn(arn: str) -> int:
    """
    Example::

        >>> extract_alias_from_arn("arn:aws:states:us-east-1:123456789012:stateMachine:HelloWorld:LIVE")
        'LIVE'
    """
    return int(arn.split(":")[-1])


def alias_dct_to_alias_name(alias_list: T.List[dict]) -> T.List[int]:
    """
    Convert a list of state machine alias detail dict to a list of
    alias name.
    """
    return [extract_alias_from_arn(dct["stateMachineAliasArn"]) for dct in alias_list]


def to_route_config_dict_view(
    route_config_list_view: T.List[dict],
) -> T.Dict[str, int]:
    """
    AWS API returns the route configuration as a list of dict::

        [
            {
                'stateMachineVersionArn': 'string',
                'weight': 123
            },
        ]

    We would like to convert it into a dict to make it easier to compare.
    """
    return {d["stateMachineVersionArn"]: d["weight"] for d in route_config_list_view}


def to_route_config_list_view(route_config_dict_view: T.Dict[str, int]) -> T.List[dict]:
    return [
        {"stateMachineVersionArn": k, "weight": v}
        for k, v in route_config_dict_view.items()
    ]


def get_alias_routing_config(
    sfn_client: "SFNClient",
    state_machine_alias_arn: str,
) -> T.Dict[int, int]:
    """
    The original describe_state_machine_alias API returns in this format::

        {
            ...,
            'routingConfiguration': [
                {
                    'stateMachineVersionArn': 'arn:...:name:2',
                    'weight': 80
                },
                {
                    'stateMachineVersionArn': 'arn:...:name:1',
                    'weight': 20
                },
            ],
            ...
        }

    We would like to convert into a dict to show the version and weight::

        {2: 80, 1: 20}

    :param sfn_client: ``boto3.client("stepfunctions")`` object
    """
    response = describe_state_machine_alias(sfn_client, state_machine_alias_arn)
    route_config_list_view = response.get("routingConfiguration", [])
    route_config_dict_view = to_route_config_dict_view(route_config_list_view)
    return {
        extract_version_from_arn(arn): weight
        for arn, weight in route_config_dict_view.items()
    }


def deploy_alias(
    sfn_client: "SFNClient",
    state_machine_arn: str,
    alias: str,
    description: T.Optional[str] = None,
    version1: T.Optional[T.Union[str, int]] = None,
    version2: T.Optional[T.Union[str, int]] = None,
    version2_percentage: T.Optional[int] = None,
    delay: int = 0,
) -> T.Tuple[bool, T.Optional[T.Dict[int, int]]]:
    """
    Point the alias to the given version or split traffic between two versions.

    :param sfn_client: ``boto3.client("stepfunctions")`` object
    :param state_machine_arn: state machine name
    :param alias: alias name
    :param description: description of the alias
    :param version1: the main version of the alias; if not specified, use $LATEST
    :param version2: the secondary version of the alias; if not specified, then
        the version1 will have 100% traffic; if specified, then version2_percentage
        also has to be specified.
    :param version2_percentage: if version2 is specified, then it has to be a
        value between 1 - 99.
    :param delay: the delay in seconds to wait before doing any deployment,
        because your previous deployment may take time to finish.

    :return: a tuple of two items; first item is a boolean flag to indicate
        whether a creation or update is performed; second item is the alias
        revision id, if creation or update is not performed, then return None.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/describe_state_machine_alias.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/create_state_machine_alias.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/update_state_machine_alias.html
    """
    if delay:  # pragma: no cover
        time.sleep(delay)

    # find out the target version and resolve routing configuration
    if version1 is None:
        last_published_version = get_last_published_version(
            sfn_client, state_machine_arn
        )
        if last_published_version is None:  # pragma: no cover
            raise ValueError(
                "You don't have any published version yet, "
                "you cannot create an alias without a published version."
            )
        else:
            version1 = str(last_published_version)
    else:
        version1 = str(version1)

    if version2 is not None:
        version2 = str(version2)
        if not (1 <= version2_percentage <= 99):  # pragma: no cover
            raise ValueError("version2 percentage has to be between 1 and 99.")
        target_routing_dict_view = {
            f"{state_machine_arn}:{version1}": 100 - version2_percentage,
            f"{state_machine_arn}:{version2}": version2_percentage,
        }
    else:
        target_routing_dict_view = {f"{state_machine_arn}:{version1}": 100}

    target_routing_config = {
        extract_version_from_arn(arn): weight
        for arn, weight in target_routing_dict_view.items()
    }

    create_or_update_alias_kwargs = dict(
        routingConfiguration=to_route_config_list_view(target_routing_dict_view),
    )
    if description:  # pragma: no cover
        create_or_update_alias_kwargs["description"] = description

    try:
        # check if the alias exists
        response = sfn_client.describe_state_machine_alias(
            stateMachineAliasArn=f"{state_machine_arn}:{alias}",
        )
        # if exists, compare the current live version with the target version
        current_routing_list_view = response.get("routingConfiguration", {})
        current_routing_dict_view = to_route_config_dict_view(current_routing_list_view)
        # update the target version
        if current_routing_dict_view != target_routing_dict_view:
            create_or_update_alias_kwargs[
                "stateMachineAliasArn"
            ] = f"{state_machine_arn}:{alias}"
            res = sfn_client.update_state_machine_alias(**create_or_update_alias_kwargs)
            return True, target_routing_config
        else:
            return False, None
    except botocore.exceptions.ClientError as e:
        # if not exists, create it
        if e.response["Error"]["Code"] == "ResourceNotFound":
            create_or_update_alias_kwargs["name"] = alias
            res = sfn_client.create_state_machine_alias(**create_or_update_alias_kwargs)
            return True, target_routing_config
        else:  # pragma: no cover
            raise e


def delete_alias(
    sfn_client: "SFNClient",
    state_machine_alias_arn: str,
) -> T.Optional[dict]:
    """
    An idempotent version of the original API.

    :param sfn_client: ``boto3.client("stepfunctions")`` object
    """
    try:
        return sfn_client.delete_state_machine_alias(
            stateMachineAliasArn=state_machine_alias_arn,
        )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFound":
            return None
        else:  # pragma: no cover
            raise e
