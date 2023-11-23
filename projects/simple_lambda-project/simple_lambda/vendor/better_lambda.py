# -*- coding: utf-8 -*-

import typing as T
from datetime import datetime, timezone
from boto_session_manager import BotoSesManager


LATEST = "$LATEST"


def publish_version(
    bsm: BotoSesManager,
    func_name: str,
) -> T.Tuple[bool, str]:
    """
    Publish a new version. This API is idempotent, i.e. if the $LATEST
    version is already the latest published version, then nothing will happen.

    :return: a tuple of two items, first item is a boolean flag to indicate
        that if a new version is created. the second item is the version id.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/publish_version.html
    """
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    # note that the publish_version will be a dry run if the $LATEST version
    # is the same as the last published version. we need to use the ``last_modified``
    # to identify if it is a dry run.
    res = bsm.lambda_client.publish_version(FunctionName=func_name)
    last_modified = datetime.strptime(res["LastModified"], "%Y-%m-%dT%H:%M:%S.%f%z")
    if utc_now > last_modified:
        is_new_version_created = False
    else:
        is_new_version_created = True
    version = res["Version"]
    return is_new_version_created, version


def deploy_alias(
    bsm: BotoSesManager,
    func_name: str,
    alias: str,
    description: T.Optional[str] = None,
    version1: T.Optional[str] = None,
    version2: T.Optional[str] = None,
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
    target_version = LATEST if version1 is None else version1
    if version2 is not None:
        if not (0.01 <= version2_percentage <= 0.99):
            raise ValueError("version2 percentage has to be between 0.01 and 0.99.")
        if target_version == LATEST:
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
    if description:
        create_or_update_alias_kwargs["Description"] = description
    # if routing_config:
    create_or_update_alias_kwargs["RoutingConfig"] = routing_config
    print(create_or_update_alias_kwargs)

    try:
        # check if the alias exists
        response = bsm.lambda_client.get_alias(
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
            res = bsm.lambda_client.update_alias(**create_or_update_alias_kwargs)
            return True, res["RevisionId"]
        else:
            return False, None
    except Exception as e:
        # if not exists, create it
        if "Cannot find alias arn" in str(e):
            res = bsm.lambda_client.create_alias(**create_or_update_alias_kwargs)
            return True, res["RevisionId"]
        else:  # pragma: no cover
            raise e


# test this module locally
if __name__ == "__main__":
    aws_profile = "awshsh_app_dev_us_east_1"
    lbd_func_name = "version_alias_test"
    alias = "LIVE"

    bsm = BotoSesManager(profile_name=aws_profile)

    # is_new_version_created, version = publish_version(bsm=bsm, func_name=lbd_func_name)
    # print(is_new_version_created, version)

    # is_alias_deployed, revision_id = deploy_alias(
    #     bsm=bsm,
    #     func_name=lbd_func_name,
    #     alias=alias,
    #     version1="1",
    #     version2="2",
    #     version2_percentage=0.1,
    # )
    # print(is_alias_deployed, revision_id)
