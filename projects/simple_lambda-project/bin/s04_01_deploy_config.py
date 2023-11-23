#!/usr/bin/env python
# -*- coding: utf-8 -*-

from automation.config import deploy_config

from simple_lambda.boto_ses import bsm
from simple_lambda.config.init import config


deploy_config(
    config=config,
    bsm=bsm,
    check=True,
)
