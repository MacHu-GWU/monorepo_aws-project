# -*- coding: utf-8 -*-

from pathlib import Path

from boto_session_manager import BotoSesManager
import aws_ops_alpha.api as aws_ops_alpha

# ------------------------------------------------------------------------------
# Enter your configuration below
# ------------------------------------------------------------------------------
# define project name, github organization, and github repository
project_name = "monorepo_aws"
github_org = "MacHu-GWU"
github_repo = f"{project_name}-project"

# define multi aws account setup
devops_aws_profile = "bmt_app_devops_us_east_1"
sbx_aws_profile = "bmt_app_dev_us_east_1"
tst_aws_profile = "bmt_app_test_us_east_1"
prd_aws_profile = "bmt_app_prod_us_east_1"

# make sure the order of environment name is aligned
workload_env_list = [
    "sbx",
    "tst",
    "prd",
]
workload_aws_profile_list = [
    sbx_aws_profile,
    tst_aws_profile,
    prd_aws_profile,
]

# read github personal access token from file
github_pac = (
    Path.home()
    .joinpath(".github", "pac", "MacHu-GWU-Full-Repo-Access.txt")
    .read_text()
    .strip()
)

# --------------------------------------------------------------------------
# Don't touch the code below until ``Run bootstrap scripts``
# --------------------------------------------------------------------------
project_name_slug = project_name.replace("_", "-")
project_name_snake = project_name.replace("-", "_")


def get_iam_resource_name(
    env_name: str,
    aws_region: str,
) -> str:
    return f"{project_name_snake}-{env_name}-deployer-{aws_region}"


if __name__ == "__main__":
    bsm_devops = BotoSesManager(profile_name=devops_aws_profile)

    workload_bsm_list = [
        BotoSesManager(profile_name=aws_profile)
        for aws_profile in workload_aws_profile_list
    ]

    github_stack_name = f"{project_name_slug}-github-oidc"
    gh_action_role_name = f"{project_name_slug}-github-oidc"
    # use this if it is first time to setup GitHub OIDC connection in your AWS Account
    # oidc_provider_arn = ""
    # use this if it is NOT first time to setup GitHub OIDC connection in your AWS Account
    oidc_provider_arn = f"arn:aws:iam::{bsm_devops.aws_account_id}:oidc-provider/token.actions.githubusercontent.com"

    workload_account_iam_policy_document = {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}],
    }

    devops_stack_name = f"{project_name_slug}-devops-deployer-us-east-1"
    devops_policy_name = f"{project_name_snake}-devops-us-east-1"

    artifacts_s3_bucket = "bmt-app-devops-us-east-1-artifacts"
    docs_s3_bucket = "bmt-app-devops-us-east-1-doc-host"

    workload_account_iam_permission_setup_list = [
        aws_ops_alpha.boostrap.multi_account.WorkloadAccountIamPermissionSetup(
            bsm=bsm,
            stack_name=get_iam_resource_name(env_name, bsm.aws_region).replace(
                "_",
                "-",
            ),
            role_name=get_iam_resource_name(env_name, bsm.aws_region),
            policy_name=get_iam_resource_name(env_name, bsm.aws_region),
            policy_document=workload_account_iam_policy_document,
        )
        for bsm, env_name in zip(workload_bsm_list, workload_env_list)
    ]

    workload_account_bsm_setup_list = [
        aws_ops_alpha.boostrap.github_action.WorkloadAccountBotoSesManagerSetup(
            bsm=bsm,
            env_name=env_name,
        )
        for bsm, env_name in zip(workload_bsm_list, workload_env_list)
    ]

    # ------------------------------------------------------------------------------
    # Wrapper function to keep the main function clean
    # ------------------------------------------------------------------------------
    def run_setup_cdk_bootstrap():
        aws_ops_alpha.boostrap.multi_account.setup_cdk_bootstrap(
            bsm_devops=bsm_devops,
            workload_bsm_list=workload_bsm_list,
        )

    def run_setup_github_action_open_id_connection():
        aws_ops_alpha.boostrap.github_action.setup_github_action_open_id_connection(
            bsm_devops=bsm_devops,
            stack_name=github_stack_name,
            github_org=github_org,
            github_repo=github_repo,
            gh_action_role_name=gh_action_role_name,
            oidc_provider_arn=oidc_provider_arn,
        )

    def run_setup_cross_account_iam_permission():
        aws_ops_alpha.boostrap.multi_account.setup_cross_account_iam_permission(
            bsm_devops=bsm_devops,
            devops_stack_name=devops_stack_name,
            devops_role_name=gh_action_role_name,
            devops_policy_name=devops_policy_name,
            workload_account_iam_permission_setup_list=workload_account_iam_permission_setup_list,
        )

    def run_setup_devops_account_s3_bucket():
        aws_ops_alpha.boostrap.multi_account.setup_devops_account_s3_bucket(
            bsm_devops=bsm_devops,
            artifacts_s3_bucket=artifacts_s3_bucket,
            docs_s3_bucket=docs_s3_bucket,
            workload_account_iam_permission_setup_list=workload_account_iam_permission_setup_list,
            artifacts_s3_prefix=f"projects/{project_name}/",
            docs_s3_prefix=f"projects/{project_name}/",
            white_list_your_ip=True,
        )

    def run_setup_github_repository_settings():
        aws_ops_alpha.boostrap.github_action.setup_github_repository_settings(
            pac=github_pac,
            github_org=github_org,
            github_repo=github_repo,
            bsm_devops=bsm_devops,
            workload_account_bsm_setup_list=workload_account_bsm_setup_list,
        )

    def run_teardown_cdk_bootstrap():
        aws_ops_alpha.boostrap.multi_account.teardown_cdk_bootstrap(
            bsm_devops=bsm_devops,
            workload_bsm_list=workload_bsm_list,
        )

    def run_teardown_github_action_open_id_connection():
        aws_ops_alpha.boostrap.github_action.teardown_github_action_open_id_connection(
            bsm_devops=bsm_devops,
            stack_name=github_stack_name,
        )

    def run_teardown_cross_account_iam_permission():
        aws_ops_alpha.boostrap.multi_account.teardown_cross_account_iam_permission(
            bsm_devops=bsm_devops,
            devops_stack_name=devops_stack_name,
            devops_role_name=gh_action_role_name,
            devops_policy_name=devops_policy_name,
            workload_account_iam_permission_setup_list=workload_account_iam_permission_setup_list,
        )

    def run_teardown_github_repository_settings():
        aws_ops_alpha.boostrap.github_action.teardown_github_repository_settings(
            pac=github_pac,
            github_org=github_org,
            github_repo=github_repo,
            workload_env_list=workload_env_list,
        )

    # --------------------------------------------------------------------------
    # Run bootstrap scripts
    # --------------------------------------------------------------------------
    # run_setup_cdk_bootstrap()
    # run_setup_github_action_open_id_connection()
    # run_setup_cross_account_iam_permission()
    # run_setup_devops_account_s3_bucket()
    # run_setup_github_repository_settings()

    # run_teardown_cross_account_iam_permission()
    # run_teardown_github_action_open_id_connection()
    # run_teardown_cdk_bootstrap()
    # run_teardown_github_repository_settings()

    pass
