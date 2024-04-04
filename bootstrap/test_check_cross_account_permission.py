# -*- coding: utf-8 -*-

"""
This script test the cross account IAM permission in GitHub Action using OIDC.
It is used in GitHub action only, it won't work on local machine because it cannot
assume the GitHub Action OIDC principal.
"""

import os
from boto_session_manager import BotoSesManager
from cross_aws_account_iam_role.api import (
    IamRoleArn,
    print_account_info,
)
from run_bootstrap import (
    get_iam_resource_name,
    workload_env_list,
)

print("the devops (CI/CD) IAM entity:")

print("--- Test the 'devops' IAM Role")
bsm = BotoSesManager()
print_account_info(bsm)

aws_region = "us-east-1"

for env_name in workload_env_list:
    aws_account_id = os.environ[f"{env_name.upper()}_AWS_ACCOUNT_ID"]
    masted_account_id = aws_account_id[:4] + '****' + aws_account_id[-4:]
    print(f"--- Test the {env_name!r} ({masted_account_id}) deployer IAM Role")
    # note: we assume the workload environment and devops environment are in the
    # same aws region, this may not true in your setup
    role_name = get_iam_resource_name(env_name, aws_region)
    bsm_assume_role = bsm.assume_role(
        role_arn=IamRoleArn(
            account=aws_account_id,
            name=role_name,
        ).arn,
        duration_seconds=900,
    )
    print_account_info(bsm_assume_role)
