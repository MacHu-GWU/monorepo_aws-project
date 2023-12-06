#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_lambda.ops.deploy import deploy_app

deploy_app(check=True)

# from automation.deploy import deploy_app
#
# from simple_lambda.paths import dir_cdk
# from simple_lambda.boto_ses import bsm
# from simple_lambda.config.init import EnvEnum, config
#
#
# deploy_app(
#     bsm=bsm,
#     config=config,
#     s3dir_lambda=config.env.s3dir_lambda,
#     tags=config.env.aws_tags,
#     dir_cdk=dir_cdk,
#     stack_name=config.env.cloudformation_stack_name,
#     prod_env_name=EnvEnum.prd.value,
#     env_name=config.env.env_name,
#     check=True,
# )
