# -*- coding: utf-8 -*-

"""
Update chalice config file based on project config management system.

We have our own project level configuration, and we don't want to manually
copy and paste data to chalice config. We create this script to automatically
sync the project config to the chalice config. Because our project is not only
about Lambda Function.

.. note::

    The chalice config file should not include any sensitive data. If you need
    to access sensitive data from lambda function, please use parameter store.
"""

# standard library
import json

# third party
from simple_lbd_agw_chalice.vendor.hashes import hashes
from config_patterns.patterns.hierarchy.api import SHARED, apply_shared_value

# project python library
from simple_lbd_agw_chalice.boto_ses import boto_ses_factory
from simple_lbd_agw_chalice.git import git_repo
from simple_lbd_agw_chalice.paths import (
    dir_lambda_app_vendor_python_lib,
    path_lambda_app_py,
    path_chalice_config,
)

from simple_lbd_agw_chalice.config.api import config
from simple_lbd_agw_chalice.iac.exports import StackExports

env_name = config.env.env_name
env = config.env

stages = dict()
source_sha256 = hashes.of_paths(
    [
        path_lambda_app_py,
        dir_lambda_app_vendor_python_lib,
    ]
)

# note: avoid hard cording any value here, use the project config instead.
chalice_config_json_data = {
    SHARED: {
        "stages.*.manage_iam_role": False,
    },
    "version": "2.0",
    "app_name": config.env.chalice_app_name,
    "stages": {},
}

bsm = boto_ses_factory.get_env_bsm(env_name)

env_vars = env.env_vars
env_vars["SOURCE_SHA256"] = source_sha256
env_vars["GIT_COMMIT_ID"] = git_repo.git_commit_id
env_vars["CONFIG_VERSION"] = config.version

tags = env.workload_aws_tags
tags["tech:source_sha256"] = source_sha256
tags["tech:git_commit_version"] = git_repo.git_commit_id
tags["tech:config_version"] = config.version

stack_export = StackExports(env_name=env_name)
stack_export.load(bsm.cloudformation_client)
chalice_config_json_data["stages"][env_name] = {
    "api_gateway_stage": env_name,
    "iam_role_arn": stack_export.get_iam_role_for_lambda_arn(),
    # note: even though we have the layers defined for each lambda function
    # you still need to declare it on stage level. otherwise, chalice will not use any layer
    "layers": list(env.lambda_functions.values())[0].get_layer_arns(boto_ses_factory.bsm_devops),
    "lambda_functions": {
        lbd_func.short_name: {
            "lambda_timeout": lbd_func.timeout,
            "lambda_memory_size": lbd_func.memory,
            "layers": list(env.lambda_functions.values())[0].get_layer_arns(boto_ses_factory.bsm_devops),
        }
        for lbd_func in env.lambda_functions.values()
    },
    "environment_variables": env_vars,
    "tags": tags,
}

chalice_config_json_data_merged = apply_shared_value(chalice_config_json_data)

path_chalice_config.write_text(json.dumps(chalice_config_json_data, indent=4))
