# -*- coding: utf-8 -*-

"""
Bootstrap for GitHub Action.
"""

# --- standard library
import typing as T
from textwrap import dedent

# --- third party library (include vendor)
import aws_cloudformation.api as aws_cf
import gh_action_open_id_in_aws.api as gh_action_open_id_in_aws

# --- modules from this project
from ...constants import AwsTagNameEnum

# --- modules from this submodule

# --- type hint
if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager


def setup_github_action_open_id_connection(
    bsm_devops: "BotoSesManager",
    stack_name: str,
    github_org: str,
    github_repo: str,
    gh_action_role_name: str,
    oidc_provider_arn: str = "",
):
    """
    The OpenID Connect (OIDC) identity provider that allows the GitHub Actions
    to assume the role in the DevOps account.
    """
    with bsm_devops.awscli():
        gh_action_open_id_in_aws.setup_github_action_open_id_connection_in_aws(
            aws_profile=None,
            stack_name=stack_name,
            github_org=github_org,
            github_repo=github_repo,
            role_name=gh_action_role_name,
            oidc_provider_arn=oidc_provider_arn,
            tags={
                AwsTagNameEnum.tech_project_name.value: "monorepo_aws",
                AwsTagNameEnum.tech_env_name: "devops sbx tst prd",
                AwsTagNameEnum.tech_description: (
                    "setup Github Action open id connection in AWS "
                    "so that Github Action can assume an IAM role to do deployment"
                ),
            },
        )

    print(
        dedent(
            """
    Note that the created IAM role won't have any permission, you need to configure it yourself. 
    
    Usually, GitHub action is used for CI/CD, you may need the following permissions to perform common CI/CD tasks:
    
    1. Manage (Create / Update / Delete) IAM Role / Policy
    2. Manage (Create / Update / Delete) AWS CloudFormation stack.
    3. Manage (Create / Update / Delete) AWS S3 Bucket to read / write deployment artifacts.
    4. Manage (Create / Update / Delete) AWS Parameter Store to read and write parameters.
    5. Manage (Create / Update / Delete) AWS ECR to push and pull container images and share it to workload AWS accounts.
    6. Manage (Create / Update / Delete) AWS EC2 AMI and share it to workload AWS accounts.
    7. Manage (Create / Update / Delete) AWS SNS Topic to send notifications.
    """
        )
    )


def teardown_github_action_open_id_connection(
    bsm_devops: "BotoSesManager",
    stack_name: str,
):
    """
    Remove the OpenID Connect (OIDC) identity provider that allows the GitHub Actions
    to assume the role in the DevOps account.
    """
    aws_cf.remove_stack(
        bsm=bsm_devops,
        stack_name=stack_name,
        skip_prompt=False,
    )
