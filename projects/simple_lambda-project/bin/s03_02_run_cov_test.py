#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_lambda.boto_ses import boto_ses_factory
print(boto_ses_factory.bsm_devops.aws_account_id[:4])
for bsm in boto_ses_factory.workload_bsm_list:
    print(bsm.aws_account_id[:4])
from simple_lambda.ops import build_lambda_source, run_cov_test

build_lambda_source(verbose=False)
run_cov_test(check=True)
