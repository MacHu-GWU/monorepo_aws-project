# -*- coding: utf-8 -*-

import typing as T
import json
import enum
import dataclasses
from pathlib import Path


class EnvNameEnum(str, enum.Enum):
    sbx = "sbx"
    tst = "tst"
    prd = "prd"


@dataclasses.dataclass
class Grantee:
    """
    The IAM principal to grant cross account permission for the deployment,
    usually it is the IAM principal of the CI/CD.

    It has to exists. This script will not create it for you.

    :param type: type of the grantee, could be one of the following:
        "root" for the entire AWS account,
        "group" for IAM group,
        "user" for IAM User,
        "role" for IAM Role,
    :param kwargs: the constructor arguments for the grantee, if it is "root",
        then it should be empty dict, otherwise, it should be
        {"name": "iam_entity_name"}.
    """

    type: str = dataclasses.field()
    kwargs: dict = dataclasses.field()


@dataclasses.dataclass
class DevOpsAwsAccount:
    """
    Represents an AWS account for the devops works, usually it is the account
    that runs the CI/CD and deploy the application to other AWS accounts.

    :param aws_profile: the aws profile to create necessary resources for
        cross account deployment
    :param grantee: see :class:`Grantee`
    :param grantee_policy_name: the grantee policy name for cross account deployment
    """

    aws_profile: str = dataclasses.field()
    grantee: Grantee = dataclasses.field()
    grantee_policy_name: str = dataclasses.field()


@dataclasses.dataclass
class EnvironmentAwsAccount:
    """
    Represents an AWS account for a specific environment (sbx, tst, prd).

    :param env_name: the name of the environment (sbx, tst, prd)
    :param aws_profile: the aws profile to create necessary resources for
        cross account deployment
    :param aws_account_id: the aws account id of the deployment target account
    :param owner_role_name: the assumed role name for cross account deployment
    :param owner_policy_name: the assumed role policy name for cross account deployment
    :param owner_policy_document: the assumed role policy document for cross account
        deployment, it defines the deployer's permissions in the target account
    """

    env_name: str = dataclasses.field()
    aws_profile: str = dataclasses.field()
    aws_account_id: str = dataclasses.field()
    owner_role_name: str = dataclasses.field()
    owner_policy_name: str = dataclasses.field()
    owner_policy_document: dict = dataclasses.field()


@dataclasses.dataclass
class Config:
    python_version_major: int = dataclasses.field()
    python_version_minor: int = dataclasses.field()
    cross_account_permission_deploy_name: str = dataclasses.field()
    devops_aws_account: DevOpsAwsAccount = dataclasses.field()
    environment_aws_accounts: T.List[EnvironmentAwsAccount] = dataclasses.field()

    @classmethod
    def load(cls, path: Path):
        data = json.loads(path.read_text())
        data["devops_aws_account"]["grantee"] = Grantee(
            **data["devops_aws_account"]["grantee"]
        )
        data["devops_aws_account"] = DevOpsAwsAccount(**data["devops_aws_account"])
        data["environment_aws_accounts"] = [
            EnvironmentAwsAccount(**dct)
            for dct in data.get("environment_aws_accounts", [])
        ]
        return cls(**data)
