# -*- coding: utf-8 -*-

import subprocess

import boto3

from ..config_init import config


def bootstrap_one_aws_account(aws_profile: str):
    boto_ses = boto3.session.Session(profile_name=aws_profile)
    aws_account_id = boto_ses.client("sts").get_caller_identity()["Account"]
    aws_region = boto_ses.region_name
    args = [
        "cdk",
        "bootstrap",
        f"aws://{aws_account_id}/{aws_region}",
        "--profile",
        aws_profile,
    ]
    subprocess.run(args, check=True)


def main():
    bootstrap_one_aws_account(config.devops_aws_account.aws_profile)
    for environment_aws_account in config.environment_aws_accounts:
        bootstrap_one_aws_account(environment_aws_account.aws_profile)
