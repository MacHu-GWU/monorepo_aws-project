#!/usr/bin/env python
# -*- coding: utf-8 -*-

from automation.build import build_lambda_source

from simple_lambda.boto_ses import boto_ses_factory
from simple_lambda.config.init import config

build_lambda_source(
    bsm=boto_ses_factory.bsm_devops,
    s3dir_lambda=config.env.s3dir_lambda,
    tags=config.env.aws_tags,
    verbose=False,
)
