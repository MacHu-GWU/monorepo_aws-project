# -*- coding: utf-8 -*-

from simple_cdk1.boto_ses import boto_ses_factory
from simple_cdk1.config.api import config, EnvNameEnum

bsm_collection = {
    "all": boto_ses_factory.bsm_devops,
    EnvNameEnum.devops.value: boto_ses_factory.bsm_devops,
    EnvNameEnum.sbx.value: boto_ses_factory.bsm_sbx,
    EnvNameEnum.tst.value: boto_ses_factory.bsm_tst,
    EnvNameEnum.prd.value: boto_ses_factory.bsm_prd,
}
config.deploy(bsm=bsm_collection, parameter_with_encryption=True)
# config.delete(bsm=bsm_collection, use_parameter_store=True)
