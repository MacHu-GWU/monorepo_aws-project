#!/usr/bin/env python
# -*- coding: utf-8 -*-

from automation.build import build_lambda_source

from simple_lambda.boto_ses import bsm
from simple_lambda.config.init import config


build_lambda_source(
    bsm=bsm,
    s3dir_lambda=config.env.s3dir_lambda,
    tags=config.env.aws_tags,
    verbose=False,
)
