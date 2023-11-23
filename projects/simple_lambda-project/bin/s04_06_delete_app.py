#!/usr/bin/env python
# -*- coding: utf-8 -*-

from automation.deploy import delete_app

from simple_lambda.paths import dir_cdk
from simple_lambda.boto_ses import bsm
from simple_lambda.config.init import EnvEnum, config


delete_app(
    bsm=bsm,
    dir_cdk=dir_cdk,
    stack_name=config.env.cloudformation_stack_name,
    prod_env_name=EnvEnum.prd.value,
    env_name=config.env.env_name,
    check=True,
)
