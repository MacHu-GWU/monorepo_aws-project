#!/usr/bin/env python
# -*- coding: utf-8 -*-

from automation.build import build_lambda_source_only
from automation.tests import run_int_test

from simple_lambda.config.init import EnvEnum, config

build_lambda_source_only(verbose=False)
run_int_test(
    prod_env_name=EnvEnum.prd.value,
    env_name=config.env.env_name,
    check=True,
)
