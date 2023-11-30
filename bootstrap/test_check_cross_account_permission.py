# -*- coding: utf-8 -*-

"""
This script test the cross account IAM permission in GitHub Action using OIDC.
"""

import os
from boto_session_manager import BotoSesManager
from cross_aws_account_iam_role.api import (
    IamRoleArn,
    print_account_info,
)
from python_lib.config_init import config

print("the devops (CI/CD) IAM entity:")

bsm = BotoSesManager()
print_account_info(bsm)

workload_aws_account_id_list = [
    os.environ["SBX_AWS_ACCOUNT_ID"],
    os.environ["TST_AWS_ACCOUNT_ID"],
    os.environ["PRD_AWS_ACCOUNT_ID"],
]
for aws_account_id, workload_aws_account in zip(
    workload_aws_account_id_list,
    config.cross_account_iam_permission.workload_aws_accounts,
):
    bsm_assume_role = bsm.assume_role(
        role_arn=IamRoleArn(
            account=aws_account_id,
            name=workload_aws_account.owner_role_name,
        ).arn,
        duration_seconds=900,
    )
    print_account_info(bsm_assume_role)
