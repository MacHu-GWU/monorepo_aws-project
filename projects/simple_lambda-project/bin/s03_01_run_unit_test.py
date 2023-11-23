#!/usr/bin/env python
# -*- coding: utf-8 -*-

from automation.build import build_lambda_source_only
from automation.tests import run_unit_test

build_lambda_source_only(verbose=False)
run_unit_test(check=True)
