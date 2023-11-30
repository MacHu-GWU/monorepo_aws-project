# -*- coding: utf-8 -*-

"""
This module should be zero dependency, so that it can be used in bootstrap.
"""

import typing as T
import json
import enum
import dataclasses
from pathlib import Path
from functools import cached_property

try:
    from boto_session_manager import BotoSesManager
except ImportError:
    pass


@dataclasses.dataclass
class Base:
    @classmethod
    def from_dict(cls, dct: dict):
        return cls(**dct)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class GitHubActionOpenIdConnection(Base):
    """
    The OpenID Connect (OIDC) identity provider that allows the GitHub Actions
    to assume the role in the target account.

    :param aws_profile: the aws profile to set up the OpenID Connect (OIDC)
        identity provider in the target account.
    :param stack_name: the cloudformation stack name to set up the OpenID Connect
    :param github_org: the GitHub organization name trusted by the IAM role
    :param github_repo: the GitHub repository name trusted by the IAM role,
        could be "*"
    :param role_name: the IAM role name to be assumed by the GitHub Actions
    """

    aws_profile: str = dataclasses.field()
    stack_name: str = dataclasses.field()
    github_org: str = dataclasses.field()
    github_repo: str = dataclasses.field()
    role_name: str = dataclasses.field()


class EnvNameEnum(str, enum.Enum):
    sbx = "sbx"
    tst = "tst"
    prd = "prd"


@dataclasses.dataclass
class Grantee(Base):
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


class AwsAccountMixin:
    @cached_property
    def bsm(self) -> "BotoSesManager":
        return BotoSesManager(profile_name=self.aws_profile)

    @property
    def aws_account_id(self) -> str:
        return self.bsm.aws_account_id


@dataclasses.dataclass
class DevOpsAwsAccount(Base, AwsAccountMixin):
    """
    Represents an AWS account for the devops works, usually it is the account
    that runs the CI/CD and deploy the application to other AWS accounts.

    :param aws_profile: the aws profile to create necessary resources for
        cross account deployment
    :param stack_name: cloudformation stack name to set up necessary resource
        for the devops AWS account.
    :param grantee: see :class:`Grantee`
    :param grantee_policy_name: the grantee policy name for cross account deployment
    """

    aws_profile: str = dataclasses.field()
    stack_name: str = dataclasses.field()
    grantee: Grantee = dataclasses.field()
    grantee_policy_name: str = dataclasses.field()

    @classmethod
    def from_dict(cls, dct: dict):
        dct["grantee"] = Grantee.from_dict(dct["grantee"])
        return cls(**dct)


@dataclasses.dataclass
class WorkloadAwsAccount(Base, AwsAccountMixin):
    """
    Represents an AWS account for a specific environment (sbx, tst, prd).

    :param env_name: the name of the environment (sbx, tst, prd)
    :param aws_profile: the aws profile to create necessary resources for
        cross account deployment
    :param stack_name: cloudformation stack name to set up necessary resource
        for the workload AWS account.
    :param owner_role_name: the assumed role name for cross account deployment
    :param owner_policy_name: the assumed role policy name for cross account deployment
    :param owner_policy_document: the assumed role policy document for cross account
        deployment, it defines the deployer's permissions in the target account
    """

    env_name: str = dataclasses.field()
    aws_profile: str = dataclasses.field()
    stack_name: str = dataclasses.field()
    owner_role_name: str = dataclasses.field()
    owner_policy_name: str = dataclasses.field()
    owner_policy_document: dict = dataclasses.field()


@dataclasses.dataclass
class CrossAccountIamPermission:
    """
    Represents the cross account IAM permission for the deployment.

    :param devops_aws_account: see :class:`DevOpsAwsAccount`
    :param env_aws_accounts: see :class:`EnvironmentAwsAccount`
    """

    devops_aws_account: DevOpsAwsAccount = dataclasses.field()
    workload_aws_accounts: T.List[WorkloadAwsAccount] = dataclasses.field()

    @classmethod
    def from_dict(cls, dct: dict):
        dct["devops_aws_account"] = DevOpsAwsAccount.from_dict(
            dct["devops_aws_account"]
        )
        dct["workload_aws_accounts"] = [
            WorkloadAwsAccount(**data) for data in dct["workload_aws_accounts"]
        ]
        return cls(**dct)


@dataclasses.dataclass
class Config:
    python_version_major: int = dataclasses.field()
    python_version_minor: int = dataclasses.field()
    github_action_open_id_connection: GitHubActionOpenIdConnection = dataclasses.field()
    cross_account_iam_permission: CrossAccountIamPermission = dataclasses.field()

    @classmethod
    def from_dict(cls, dct: dict):
        dct[
            "github_action_open_id_connection"
        ] = GitHubActionOpenIdConnection.from_dict(
            dct["github_action_open_id_connection"]
        )
        dct["cross_account_iam_permission"] = CrossAccountIamPermission.from_dict(
            dct["cross_account_iam_permission"]
        )
        return cls(**dct)

    @classmethod
    def load(cls, path: Path):
        data = json.loads(path.read_text())
        return cls.from_dict(data)
