# -*- coding: utf-8 -*-

import os
import pytest

from dynamodbsnaplake.boto_ses import bsm
from dynamodbsnaplake.iac.exports import StackExports
from dynamodbsnaplake.config.load import config


class TestStackExports:
    def test(self):
        stack_exports = StackExports(env_name=config.env.env_name)
        stack_exports.load(bsm.cloudformation_client)
        _ = stack_exports.get_iam_role_for_lambda_arn()
        _ = stack_exports.get_iam_role_for_sfn_arn()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
