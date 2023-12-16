#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_cdk1.ops import build_lambda_source, run_cov_test

build_lambda_source(verbose=False)
run_cov_test(check=True)
