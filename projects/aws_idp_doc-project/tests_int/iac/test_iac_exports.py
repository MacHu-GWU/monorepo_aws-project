# -*- coding: utf-8 -*-

import os
import pytest

from aws_idp_doc.boto_ses import bsm
from aws_idp_doc.iac.exports import StackExports
from aws_idp_doc.config.load import config


class TestStackExports:
    def test(self):
        stack_exports = StackExports(env_name=config.env.env_name)
        stack_exports.load(bsm.cloudformation_client)
        _ = stack_exports.get_iam_managed_policy_dummy_arn()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
