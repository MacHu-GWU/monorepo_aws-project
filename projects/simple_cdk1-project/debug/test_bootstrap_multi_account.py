# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
from simple_cdk1.vendor.aws_ops_alpha.boostrap.multi_account.api import (
    setup_cdk_bootstrap,
    teardown_cdk_bootstrap,
    WorkloadAccountIamPermissionSetup,
    setup_cross_account_iam_permission,
    teardown_cross_account_iam_permission,
    setup_devops_account_s3_bucket,
    teardown_devops_account_s3_bucket,
)

bsm_devops = BotoSesManager(profile_name="bmt_app_devops_us_east_1")
bsm_sbx = BotoSesManager(profile_name="bmt_app_dev_us_east_1")
bsm_tst = BotoSesManager(profile_name="bmt_app_test_us_east_1")
bsm_prd = BotoSesManager(profile_name="bmt_app_prod_us_east_1")

workload_bsm_list = [
    bsm_sbx,
    bsm_tst,
    bsm_prd,
]

sbx_res_name = f"monorepo-aws-sbx-deployer-{bsm_sbx.aws_region}"
tst_res_name = f"monorepo-aws-tst-deployer-{bsm_sbx.aws_region}"
prd_res_name = f"monorepo-aws-prd-deployer-{bsm_sbx.aws_region}"

workload_account_iam_policy_document = {
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}],
}

devops_role_name = "monorepo-aws-github-oidc"
devops_stack_name = "monorepo-aws-devops-deployer-us-east-1"
devops_policy_name = "monorepo_aws-devops-us-east-1"

artifacts_s3_bucket = "bmt-app-devops-us-east-1-artifacts"
docs_s3_bucket = "bmt-app-devops-us-east-1-doc-host"

workload_account_iam_permission_setup_list = [
    WorkloadAccountIamPermissionSetup(
        bsm=bsm_sbx,
        stack_name=sbx_res_name,
        role_name=sbx_res_name,
        policy_name=sbx_res_name,
        policy_document=workload_account_iam_policy_document,
    ),
    WorkloadAccountIamPermissionSetup(
        bsm=bsm_tst,
        stack_name=tst_res_name,
        role_name=tst_res_name,
        policy_name=tst_res_name,
        policy_document=workload_account_iam_policy_document,
    ),
    WorkloadAccountIamPermissionSetup(
        bsm=bsm_prd,
        stack_name=prd_res_name,
        role_name=prd_res_name,
        policy_name=prd_res_name,
        policy_document=workload_account_iam_policy_document,
    ),
]


def run_setup_cdk_bootstrap():
    setup_cdk_bootstrap(
        bsm_devops=bsm_devops,
        workload_bsm_list=workload_bsm_list,
    )


def run_setup_cross_account_iam_permission():
    setup_cross_account_iam_permission(
        bsm_devops=bsm_devops,
        devops_role_name=devops_role_name,
        devops_stack_name=devops_stack_name,
        devops_policy_name=devops_policy_name,
        workload_account_iam_permission_setup_list=workload_account_iam_permission_setup_list,
    )


def run_setup_devops_account_s3_bucket():
    setup_devops_account_s3_bucket(
        bsm_devops=bsm_devops,
        artifacts_s3_bucket=artifacts_s3_bucket,
        docs_s3_bucket=docs_s3_bucket,
        workload_account_iam_permission_setup_list=workload_account_iam_permission_setup_list,
        artifacts_s3_prefix="projects/monorepo_aws/",
        white_list_your_ip=True,
    )


def run_teardown_cdk_bootstrap():
    teardown_cdk_bootstrap(
        bsm_devops=bsm_devops,
        workload_bsm_list=workload_bsm_list,
    )


def run_teardown_cross_account_iam_permission():
    teardown_cross_account_iam_permission(
        bsm_devops=bsm_devops,
        devops_role_name=devops_role_name,
        devops_stack_name=devops_stack_name,
        devops_policy_name=devops_policy_name,
        workload_account_iam_permission_setup_list=workload_account_iam_permission_setup_list,
    )


if __name__ == "__main__":
    # run_setup_cdk_bootstrap()
    # run_setup_cross_account_iam_permission()
    # run_setup_devops_account_s3_bucket()

    # run_teardown_cross_account_iam_permission()
    # run_teardown_cdk_bootstrap()

    pass
