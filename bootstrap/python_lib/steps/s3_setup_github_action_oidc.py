# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
from gh_action_open_id_in_aws.api import setup_github_action_open_id_connection_in_aws

from ..config_init import config


def main():
    setup_github_action_open_id_connection_in_aws(
        aws_profile=config.github_action_open_id_connection.aws_profile,
        stack_name=config.github_action_open_id_connection.stack_name,
        github_org=config.github_action_open_id_connection.github_org,
        github_repo=config.github_action_open_id_connection.github_repo,
        role_name=config.github_action_open_id_connection.role_name,
        oidc_provider_arn=f"arn:aws:iam::{config.cross_account_iam_permission.devops_aws_account.aws_account_id}:oidc-provider/token.actions.githubusercontent.com",
        tags={
            "tech:project_name": "monorepo_aws",
            "tech:env_name": "devops sbx tst prd",
            "tech:description": (
                "setup Github Action open id connection in AWS "
                "so that Github Action can assume an IAM role to do deployment"
            ),
        },
    )

    bsm_devops = BotoSesManager(
        profile_name=config.github_action_open_id_connection.aws_profile
    )
    bsm_devops.iam_client.attach_role_policy(
        RoleName=config.github_action_open_id_connection.role_name,
        PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess",
    )
