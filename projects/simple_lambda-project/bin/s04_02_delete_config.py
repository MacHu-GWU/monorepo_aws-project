#!/usr/bin/env python
# -*- coding: utf-8 -*-

from automation.config import delete_config

from simple_lambda.boto_ses import bsm
from simple_lambda.config.init import config


delete_config(
    config=config,
    bsm=bsm,
    check=True,
)
