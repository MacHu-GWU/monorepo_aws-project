#!/usr/bin/env python
# -*- coding: utf-8 -*-

from automation.pyproject import pyproject_ops
from automation.git import GIT_COMMIT_ID, create_git_tag

from simple_lambda.config.init import EnvEnum, config


create_git_tag(
    tag_name=f"{pyproject_ops.package_name}-{pyproject_ops.package_version}",
    commit_id=GIT_COMMIT_ID,
    env_name=config.env.env_name,
    prod_env_name=EnvEnum.prd.value,
    check=True,
)
