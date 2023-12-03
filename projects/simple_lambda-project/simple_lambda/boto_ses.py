# -*- coding: utf-8 -*-

import dataclasses

from s3pathlib import context

from .vendor.aws_ops_alpha.api import Config, runtime, BotoSesFactory

aws_ops_alpha_config = Config(
    env_aws_profile_mapper={
        "devops": "bmt_app_devops_us_east_1",
        "sbx": "bmt_app_dev_us_east_1",
        "tst": "bmt_app_test_us_east_1",
        "prd": "bmt_app_prod_us_east_1",
    }
)


@dataclasses.dataclass
class BotoSesFactory(BotoSesFactory):
    def get_env_role_name(self, env_name: str) -> str:
        return f"monorepo_aws-{env_name}-deployer-us-east-1"


boto_ses_factory = BotoSesFactory(
    config=aws_ops_alpha_config,
    runtime=runtime,
)
bsm = boto_ses_factory.bsm

# Set default s3pathlib boto session
context.attach_boto_session(boto_ses=bsm.boto_ses)
