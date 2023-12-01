# -*- coding: utf-8 -*-

import typing as T
import os
import json
from boto_session_manager import BotoSesManager
from cross_aws_account_iam_role.api import (
    IamRootArn,
    IamUserArn,
    IamRoleArn,
    Grantee,
    Owner,
    deploy,
)
from ..config_init import config


def main():
    devops_aws_account = config.cross_account_iam_permission.devops_aws_account
    workload_aws_accounts = config.cross_account_iam_permission.workload_aws_accounts

    devops_artifacts_bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "allow IAM role on CodeCommit repos account to access this s3 bucket",
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        f"arn:aws:iam::{workload_aws_account.aws_account_id}:root"
                        for workload_aws_account in workload_aws_accounts
                    ],
                },
                "Action": [
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:GetObjectTagging",
                    "s3:GetObjectAttributes",
                ],
                "Resource": [
                    f"arn:aws:s3:::{devops_aws_account.s3bucket_artifacts}",
                    f"arn:aws:s3:::{devops_aws_account.s3bucket_artifacts}/*",
                ],
            }
        ],
    }

    devops_bsm = BotoSesManager(profile_name=devops_aws_account.aws_profile)
    devops_bsm.s3_client.put_bucket_policy(
        Bucket=devops_aws_account.s3bucket_artifacts,
        Policy=json.dumps(devops_artifacts_bucket_policy),
    )
