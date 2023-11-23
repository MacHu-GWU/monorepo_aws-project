# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
from python_lib.cross_account_iam_role_access_manager import (
    IamRoleArn,
    print_account_info,
)
from python_lib.config_init import config

print("the devops (CI/CD) IAM entity:")
bsm = BotoSesManager()
print_account_info(bsm)

for environment_aws_account in config.environment_aws_accounts:
    print(f"the {environment_aws_account.env_name!r} environment deployer IAM entity:")
    bsm_assume_role = bsm.assume_role(
        role_arn=IamRoleArn(
            account=environment_aws_account.aws_account_id,
            name=environment_aws_account.owner_role_name,
        ).arn,
        duration_seconds=900,
    )
    print_account_info(bsm_assume_role)
