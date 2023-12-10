# -*- coding: utf-8 -*-

from simple_lambda.boto_ses import boto_ses_factory
from simple_lambda.config.init import config, EnvEnum

bsm_collection = {
    "all": boto_ses_factory.bsm_devops,
    EnvEnum.sbx.value: boto_ses_factory.bsm_sbx,
    EnvEnum.tst.value: boto_ses_factory.bsm_tst,
    EnvEnum.prd.value: boto_ses_factory.bsm_prd,
}
config.deploy(bsm=bsm_collection, parameter_with_encryption=True)
# config.delete(bsm=bsm_collection, use_parameter_store=True)
