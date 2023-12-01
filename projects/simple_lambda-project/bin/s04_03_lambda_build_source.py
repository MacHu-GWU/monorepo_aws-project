#!/usr/bin/env python
# -*- coding: utf-8 -*-

from automation.build import build_lambda_source

from simple_lambda.boto_ses import get_devops_bsm
from simple_lambda.config.init import config

bsm_devops = get_devops_bsm()

build_lambda_source(
    bsm=bsm_devops,
    s3dir_lambda=config.env.s3dir_lambda,
    tags=config.env.aws_tags,
    verbose=False,
)
