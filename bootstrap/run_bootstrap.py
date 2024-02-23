# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
import aws_ops_alpha.api as aws_ops_alpha

# ------------------------------------------------------------------------------
# Enter your configuration below
# ------------------------------------------------------------------------------
bsm_devops = BotoSesManager(profile_name="bmt_app_devops_us_east_1")
bsm_sbx = BotoSesManager(profile_name="bmt_app_dev_us_east_1")
bsm_tst = BotoSesManager(profile_name="bmt_app_test_us_east_1")
bsm_prd = BotoSesManager(profile_name="bmt_app_prod_us_east_1")

workload_bsm_list = [
    bsm_sbx,
    bsm_tst,
    bsm_prd,
]

project_name = "monorepo_aws"
project_name_slug = project_name.replace("_", "-")
project_name_snake = project_name.replace("-", "_")

github_stack_name = f"{project_name_slug}-github-oidc"
github_org = "MacHu-GWU"
github_repo = f"{project_name}-project"
gh_action_role_name = f"{project_name_slug}-github-oidc"
# use this if it is first time to setup GitHub OIDC connection in your AWS Account
# oidc_provider_arn = ""
# use this if it is NOT first time to setup GitHub OIDC connection in your AWS Account
oidc_provider_arn = f"arn:aws:iam::{bsm_devops.aws_account_id}:oidc-provider/token.actions.githubusercontent.com"

sbx_res_name = f"{project_name_snake}-sbx-deployer-{bsm_sbx.aws_region}"
tst_res_name = f"{project_name_snake}-tst-deployer-{bsm_sbx.aws_region}"
prd_res_name = f"{project_name_snake}-prd-deployer-{bsm_sbx.aws_region}"

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
        bsm=bsm_sbx,
        stack_name=sbx_res_name.replace("_", "-"),
        role_name=sbx_res_name,
        policy_name=sbx_res_name,
        policy_document=workload_account_iam_policy_document,
    ),
    aws_ops_alpha.boostrap.multi_account.WorkloadAccountIamPermissionSetup(
        bsm=bsm_tst,
        stack_name=tst_res_name.replace("_", "-"),
        role_name=tst_res_name,
        policy_name=tst_res_name,
        policy_document=workload_account_iam_policy_document,
    ),
    aws_ops_alpha.boostrap.multi_account.WorkloadAccountIamPermissionSetup(
        bsm=bsm_prd,
        stack_name=prd_res_name.replace("_", "-"),
        role_name=prd_res_name,
        policy_name=prd_res_name,
        policy_document=workload_account_iam_policy_document,
    ),
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


def run_teardown_cdk_bootstrap():
    aws_ops_alpha.boostrap.multi_account.teardown_cdk_bootstrap(
        bsm_devops=bsm_devops,
        workload_bsm_list=workload_bsm_list,
    )


def run_teardown_github_action_open_id_connection():
    aws_ops_alpha.boostrap.github_action.teardown_github_aws_ops_alphaaction_open_id_connection(
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


# ------------------------------------------------------------------------------
# Run bootstrap scripts
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # run_setup_cdk_bootstrap()
    # run_setup_github_action_open_id_connection()
    # run_setup_cross_account_iam_permission()
    # run_setup_devops_account_s3_bucket()

    # run_teardown_cross_account_iam_permission()
    # run_teardown_github_action_open_id_connection()
    # run_teardown_cdk_bootstrap()

    pass
