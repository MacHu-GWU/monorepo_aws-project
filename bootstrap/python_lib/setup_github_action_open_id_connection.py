# -*- coding: utf-8 -*-

"""
This script automates the GitHub open id connect configuration in AWS.

Python >= 3.7 is required.

Requirements::

    boto_session_manager>=1.5.4,<2.0.0
    aws_cloudformation>=1.5.1,<2.0.0
"""

from pathlib import Path

from boto_session_manager import BotoSesManager
import aws_cloudformation.api as aws_cf


def setup_github_action_open_id_connection(
    aws_profile: str,
    stack_name: str,
    github_org: str,
    github_repo: str,
    role_name: str,
):
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
    bsm = BotoSesManager(profile_name=aws_profile)
    dir_here = Path(__file__).absolute().parent
    aws_cf.deploy_stack(
        bsm=bsm,
        stack_name=stack_name,
        template=dir_here.joinpath(
            "setup_github_action_open_id_connection-2023-11-26.yml"
        ).read_text(),
        parameters=[
            aws_cf.Parameter(key="GitHubOrg", value=github_org),
            aws_cf.Parameter(key="RepositoryName", value=github_repo),
            aws_cf.Parameter(key="RoleName", value=role_name),
        ],
        skip_prompt=True,
        include_named_iam=True,
        tags={
            "tech:description": "Test configure GitHub open id connect in AWS",
        },
    )


# below is an example of how to use this function
if __name__ == "__main__":
    setup_github_action_open_id_connection(
        aws_profile="bmt_app_dev_us_east_1",
        stack_name="monorepo-aws-github-open-id-connection",
        github_org="MacHu-GWU",
        github_repo="monorepo_aws-project",
        role_name="monorepo-aws-github-open-id-connection",
    )
