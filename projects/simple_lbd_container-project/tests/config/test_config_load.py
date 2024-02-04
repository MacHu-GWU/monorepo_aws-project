# -*- coding: utf-8 -*-

from simple_lbd_container.config.api import config


def test():
    # main.py
    _ = config

    _ = config.env

    # app.py
    _ = config.env.username
    _ = config.env.password
    _ = config.env.s3uri_data

    _ = config.env.s3dir_data
    _ = config.env.s3dir_source
    _ = config.env.s3dir_target
    _ = config.env.env_vars
    _ = config.env.devops_aws_tags
    _ = config.env.workload_aws_tags

    _ = config.env.s3uri_artifacts
    _ = config.env.s3uri_docs

    _ = config.env.s3dir_artifacts
    _ = config.env.s3dir_env_artifacts
    _ = config.env.s3dir_tmp
    _ = config.env.s3dir_config
    _ = config.env.s3dir_docs

    # ecr.py
    _ = config.env.ecr_repo_name

    # lbd_deploy.py
    _ = config.env.chalice_app_name
    _ = config.env.lambda_layer_name
    _ = config.env.s3dir_lambda

    # lbd_func.py
    _ = config.env.lambda_functions
    _ = config.env.lambda_function_name_list
    _ = config.env.lambda_function_list
    for shortname, lambda_function in config.env.lambda_functions.items():
        _ = lambda_function.env
        _ = lambda_function.handler
        _ = lambda_function.timeout
        _ = lambda_function.memory
        _ = lambda_function.iam_role
        _ = lambda_function.env_vars
        _ = lambda_function.layers
        _ = lambda_function.subnet_ids
        _ = lambda_function.security_group_ids
        _ = lambda_function.reserved_concurrency
        _ = lambda_function.live_version1
        _ = lambda_function.live_version2
        _ = lambda_function.live_version2_percentage

        _ = lambda_function.name
        _ = lambda_function.short_name_slug
        _ = lambda_function.short_name_snake
        _ = lambda_function.short_name_camel
        _ = lambda_function.target_live_version1

    _ = config.env.lbd_hello
    _ = config.env.lbd_s3sync

    # name.py
    _ = config.env.cloudformation_stack_name


if __name__ == "__main__":
    from simple_lbd_container.tests import run_cov_test

    run_cov_test(__file__, "simple_lbd_container.config", preview=False)
