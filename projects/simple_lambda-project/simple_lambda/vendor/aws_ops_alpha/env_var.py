# -*- coding: utf-8 -*-

"""
Manage environment variables, and provide utility method to consume them.

**About AWS Account ID in CI runtime**

Let's say you have a ``devops`` AWS account 999999999999 to host your shared
AWS resources like code artifacts, ECR images. And you have three workload
AWS account ``sbx`` (111111111111), ``tst`` (222222222222), and ``prd`` (333333333333).
Then your CI runtime should have the following environment variables:

- ``DEVOPS_AWS_ACCOUNT_ID``: 999999999999
- ``SBX_AWS_ACCOUNT_ID``: 111111111111
- ``TST_AWS_ACCOUNT_ID``: 222222222222
- ``PRD_AWS_ACCOUNT_ID``: 333333333333

If you prefer, you can use the same AWS account for devops and different workload.
You still need to specify those environment variables.
"""

import os

from .constants import DEVOPS


def get_devops_aws_account_id_in_ci() -> str:
    """
    Get devops AWS account ID in CI runtime. We assume that your store
    them in environment variables like ``DEVOPS_AWS_ACCOUNT_ID``.
    """
    return os.environ[f"{DEVOPS.upper()}_AWS_ACCOUNT_ID"]


def get_workload_aws_account_id_in_ci(env_name: str) -> str:
    """
    Get workload AWS account ID in CI runtime. We assume that your store
    them in environment variables like ``SBX_AWS_ACCOUNT_ID``.
    """
    return os.environ[f"{env_name.upper()}_AWS_ACCOUNT_ID"]
