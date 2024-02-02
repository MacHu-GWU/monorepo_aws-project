# -*- coding: utf-8 -*-

"""
Define the boto session creation setup for this project.
"""

import os
import dataclasses
from functools import cached_property

from s3pathlib import context

from .vendor.import_agent import aws_ops_alpha

from .env import EnvNameEnum, detect_current_env
from .runtime import runtime


@dataclasses.dataclass
class BotoSesFactory(aws_ops_alpha.AlphaBotoSesFactory):
    def get_env_role_arn(self, env_name: str) -> str:  # pragma: no cover
        aws_account_id = os.environ[f"{env_name.upper()}_AWS_ACCOUNT_ID"]
        return f"arn:aws:iam::{aws_account_id}:role/monorepo_aws-{env_name}-deployer-us-east-1"

    def get_env_role_session_name(self, env_name: str) -> str: # pragma: no cover
        return f"{env_name}_role_session"

    def get_current_env(self) -> str:
        return detect_current_env()

    @cached_property
    def bsm_sbx(self):
        return self.get_env_bsm(env_name=EnvNameEnum.sbx.value)

    @cached_property
    def bsm_tst(self):
        return self.get_env_bsm(env_name=EnvNameEnum.tst.value)

    # @cached_property
    # def bsm_stg(self):
    #     return self.get_env_bsm(env_name=EnvEnum.stg.value)

    @cached_property
    def bsm_prd(self):
        return self.get_env_bsm(env_name=EnvNameEnum.prd.value)

    @cached_property
    def workload_bsm_list(self):
        return [
            self.bsm_sbx,
            self.bsm_tst,
            # self.bsm_stg,
            self.bsm_prd,
        ]

    def print_who_am_i(self):  # pragma: no cover
        masked = not runtime.is_local_runtime_group
        for name, bsm in [
            ("bsm_devops", boto_ses_factory.bsm_devops),
            ("bsm_sbx", boto_ses_factory.bsm_sbx),
            ("bsm_tst", boto_ses_factory.bsm_tst),
            # ("bsm_stg", boto_ses_factory.bsm_tst),
            ("bsm_prd", boto_ses_factory.bsm_prd),
        ]:
            print(f"--- {name} ---")
            bsm.print_who_am_i(masked=masked)


boto_ses_factory = BotoSesFactory(
    runtime=runtime,
    env_to_profile_mapper={
        EnvNameEnum.devops.value: "bmt_app_devops_us_east_1",
        EnvNameEnum.sbx.value: "bmt_app_dev_us_east_1",
        EnvNameEnum.tst.value: "bmt_app_test_us_east_1",
        # EnvEnum.stg.value: "bmt_app_test_us_east_1",
        EnvNameEnum.prd.value: "bmt_app_prod_us_east_1",
    },
    default_app_env_name=EnvNameEnum.sbx.value,
)

bsm = boto_ses_factory.bsm
# ----------------------------------------------------------------------
# you can uncomment this line to force to use certain env
# from your local laptop to run application code, tests, ...
# ----------------------------------------------------------------------
# bsm = boto_ses_factory.bsm_prd

# Set default s3pathlib boto session
context.attach_boto_session(boto_ses=bsm.boto_ses)
