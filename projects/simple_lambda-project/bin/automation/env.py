# -*- coding: utf-8 -*-

"""
**Environment Definition**

Environment is basically a group of resources with specific name space.

This module automatically detect what environment we should use.
"""

import os

from .runtime import IS_CI
from .logger import logger


def find_env() -> str:
    """
    Find which environment we should deploy to.
    """
    if IS_CI:
        return os.environ["USER_ENV_NAME"]
    # if it is not in CI (on local laptop), it is always deploy to dev
    else:
        # you can uncomment this line to force to use certain env
        # from your local laptop to run automation, deployment script ...
        # return "sbx"
        if "USER_ENV_NAME" in os.environ:
            return os.environ["USER_ENV_NAME"]
        return "sbx"


CURRENT_ENV = find_env()


def print_env_info():
    logger.info(f"Current environment name is 🏢 {CURRENT_ENV!r}")
