# -*- coding: utf-8 -*-

"""
Define the boto session creation setup for this project.
"""

import os
import dataclasses
from functools import cached_property

from s3pathlib import context

import simple_lambda.vendor.aws_ops_alpha.api as aws_ops_alpha

from .env import EnvEnum
from .runtime import runtime


@dataclasses.dataclass
class BotoSesFactory(aws_ops_alpha.AlphaBotoSesFactory):
    def get_env_role_arn(self, env_name: str) -> str:
        aws_account_id = os.environ[f"{env_name.upper()}_AWS_ACCOUNT_ID"]
        return f"arn:aws:iam::{aws_account_id}:role/monorepo_aws-{env_name}-deployer-us-east-1"

    @cached_property
    def bsm_sbx(self):
        return self.get_env_bsm(env_name=EnvEnum.sbx.value)

    @cached_property
    def bsm_tst(self):
        return self.get_env_bsm(env_name=EnvEnum.tst.value)

    # @cached_property
    # def bsm_stg(self):
    #     return self.get_env_bsm(env_name=EnvEnum.stg.value)

    @cached_property
    def bsm_prd(self):
        return self.get_env_bsm(env_name=EnvEnum.prd.value)

    @cached_property
    def workload_bsm_list(self):
        return [
            self.bsm_sbx,
            self.bsm_tst,
            # self.bsm_stg,
            self.bsm_prd,
        ]


boto_ses_factory = BotoSesFactory(
    runtime=runtime,
    env_to_profile_mapper={
        aws_ops_alpha.constants.DEVOPS: "bmt_app_devops_us_east_1",
        EnvEnum.sbx.value: "bmt_app_dev_us_east_1",
        EnvEnum.tst.value: "bmt_app_test_us_east_1",
        # EnvEnum.stg.value: "bmt_app_test_us_east_1",
        EnvEnum.prd.value: "bmt_app_prod_us_east_1",
    },
    default_app_env_name=EnvEnum.sbx.value,
)
print(f"{boto_ses_factory.bsm_devops.aws_account_alias = }")

bsm = boto_ses_factory.bsm

# Set default s3pathlib boto session
context.attach_boto_session(boto_ses=bsm.boto_ses)
