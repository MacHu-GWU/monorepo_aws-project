# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
from aws_idp_doc.vendor.aws_ops_alpha.boostrap.github_action.api import (
    setup_github_action_open_id_connection,
    teardown_github_action_open_id_connection,
)

bsm_devops = BotoSesManager(profile_name="bmt_app_devops_us_east_1")
stack_name = "monorepo-aws-github-oidc"
github_org = "MacHu-GWU"
github_repo = "monorepo_aws-project"
gh_action_role_name = "monorepo-aws-github-oidc"
oidc_provider_arn = f"arn:aws:iam::{bsm_devops.aws_account_id}:oidc-provider/token.actions.githubusercontent.com"


def run_setup_github_action_open_id_connection():
    setup_github_action_open_id_connection(
        bsm_devops=bsm_devops,
        stack_name=stack_name,
        github_org=github_org,
        github_repo=github_repo,
        gh_action_role_name=gh_action_role_name,
        oidc_provider_arn=oidc_provider_arn,
    )


def run_teardown_github_action_open_id_connection():
    teardown_github_action_open_id_connection(
        bsm_devops=bsm_devops,
        stack_name=stack_name,
    )


if __name__ == "__main__":
    # run_setup_github_action_open_id_connection()
    # run_teardown_github_action_open_id_connection()
    pass
