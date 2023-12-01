# -*- coding: utf-8 -*-

import os
from s3pathlib import context
from boto_session_manager import BotoSesManager

from .runtime import IS_LOCAL, IS_CI, IS_LAMBDA


# environment aware boto session manager
if IS_LAMBDA:  # put production first
    bsm = BotoSesManager(
        region_name="us-east-1",
    )
elif IS_LOCAL:
    bsm = BotoSesManager(
        profile_name="bmt_app_dev_us_east_1",
        region_name="us-east-1",
    )
elif IS_CI:
    bsm = BotoSesManager(
        region_name="us-east-1",
    )
else:  # pragma: no cover
    raise NotImplementedError

# Set default s3pathlib boto session
context.attach_boto_session(boto_ses=bsm.boto_ses)

env_name_to_aws_profile_mapper = {
    "sbx": "bmt_app_dev_us_east_1",
    "tst": "bmt_app_test_us_east_1",
    "prd": "bmt_app_prod_us_east_1",
}


def get_devops_bsm() -> BotoSesManager:
    if IS_LOCAL:
        return BotoSesManager(
            profile_name="bmt_app_devops_us_east_1",
            region_name="us-east-1",
        )
    elif IS_CI:
        return bsm


def get_env_bsm(env_name: str) -> BotoSesManager:
    if IS_LOCAL:
        return BotoSesManager(
            profile_name=env_name_to_aws_profile_mapper[env_name],
            region_name="us-east-1",
        )
    elif IS_CI:
        aws_account_id = os.environ[f"{env_name.upper()}_AWS_ACCOUNT_ID"]
        role_name = f"monorepo_aws-{env_name}-deployer-{bsm.aws_region}"
        return bsm.assume_role(
            role_arn=f"arn:aws:iam::{aws_account_id}:role/{role_name}",
            region_name=bsm.aws_region,
        )
    else:  # pragma: no cover
        raise NotImplementedError


def get_sbx_bsm() -> BotoSesManager:
    return get_env_bsm("sbx")


def get_tst_bsm() -> BotoSesManager:
    return get_env_bsm("tst")


def get_prd_bsm() -> BotoSesManager:
    return get_env_bsm("prd")
