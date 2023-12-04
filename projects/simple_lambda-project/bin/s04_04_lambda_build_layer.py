#!/usr/bin/env python
# -*- coding: utf-8 -*-

from automation.build import build_lambda_layer

from simple_lambda.boto_ses import boto_ses_factory
from simple_lambda.config.init import config

build_lambda_layer(
    bsm_devops=boto_ses_factory.bsm_devops,
    workload_bsm_list=boto_ses_factory.workload_bsm_list,
    layer_name=config.env.lambda_layer_name,
    s3dir_lambda=config.env.s3dir_lambda,
    tags=config.env.aws_tags,
    check=True,
)
