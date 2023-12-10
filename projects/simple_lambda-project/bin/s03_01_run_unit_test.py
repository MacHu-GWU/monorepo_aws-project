#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_lambda.boto_ses import boto_ses_factory
print(boto_ses_factory.workload_bsm_list)

from simple_lambda.ops import build_lambda_source, run_unit_test

build_lambda_source(verbose=False)
run_unit_test(check=True)
