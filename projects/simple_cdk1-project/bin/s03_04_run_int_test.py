#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_cdk1.ops import build_lambda_source, run_int_test

build_lambda_source(verbose=False)
run_int_test(check=True)
