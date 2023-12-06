#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_lambda.ops.build import build_lambda_source_only
from simple_lambda.ops.tests import run_unit_test

build_lambda_source_only(verbose=False)
run_unit_test(check=True)
