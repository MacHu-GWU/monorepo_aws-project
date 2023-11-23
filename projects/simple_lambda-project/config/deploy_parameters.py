# -*- coding: utf-8 -*-

from simple_lambda.boto_ses import bsm
from simple_lambda.config.init import config

config.deploy(bsm=bsm, parameter_with_encryption=True)
# config.delete(bsm=bsm, use_parameter_store=True)
