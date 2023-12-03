# -*- coding: utf-8 -*-

from .vendor.aws_ops_alpha.api import Config, runtime, BotoSes

aws_ops_alpha_config = Config(
    env_aws_profile_mapper={
        "devops": "bmt_app_devops_us_east_1",
        "sbx": "bmt_app_dev_us_east_1",
        "tst": "bmt_app_test_us_east_1",
        "prd": "bmt_app_prod_us_east_1",
    }
)
boto_ses = BotoSes(
    config=aws_ops_alpha_config,
    runtime=runtime,
)
