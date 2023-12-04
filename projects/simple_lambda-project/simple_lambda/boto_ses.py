# -*- coding: utf-8 -*-

import dataclasses
from functools import cached_property

from s3pathlib import context

import aws_ops_alpha.api as aws_ops_alpha

from .config.define import EnvEnum
from .runtime import runtime

aws_ops_alpha_config = aws_ops_alpha.Config(
    env_aws_profile_mapper={
        aws_ops_alpha.constants.DEVOPS: "bmt_app_devops_us_east_1",
        EnvEnum.sbx.value: "bmt_app_dev_us_east_1",
        EnvEnum.tst.value: "bmt_app_test_us_east_1",
        EnvEnum.prd.value: "bmt_app_prod_us_east_1",
    }
)


@dataclasses.dataclass
class BotoSesFactory(aws_ops_alpha.BotoSesFactory):
    def get_env_role_name(self, env_name: str) -> str:
        return f"monorepo_aws-{env_name}-deployer-us-east-1"

    @cached_property
    def bsm_sbx(self):
        return self.get_app_bsm(env_name=EnvEnum.sbx.value)

    @cached_property
    def bsm_tst(self):
        return self.get_app_bsm(env_name=EnvEnum.tst.value)

    @cached_property
    def bsm_prd(self):
        return self.get_app_bsm(env_name=EnvEnum.prd.value)


boto_ses_factory = BotoSesFactory(
    config=aws_ops_alpha_config,
    runtime=runtime,
)
bsm = boto_ses_factory.bsm

# Set default s3pathlib boto session
context.attach_boto_session(boto_ses=bsm.boto_ses)
