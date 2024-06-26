# -*- coding: utf-8 -*-

from aws_idp_data_store.config.api import config


def test():
    # main.py
    _ = config

    _ = config.env

    # app.py
    _ = config.env.s3uri_data
    _ = config.env.s3dir_data
    _ = config.env.s3dir_documents_data_store
    _ = config.env.s3dir_source
    _ = config.env.s3dir_target
    _ = config.env.env_vars
    _ = config.env.devops_aws_tags
    _ = config.env.workload_aws_tags
    _ = config.env.s3dir_target

    # deploy.py
    _ = config.env.s3uri_artifacts
    _ = config.env.s3uri_docs

    _ = config.env.s3dir_artifacts
    _ = config.env.s3dir_env_artifacts
    _ = config.env.s3dir_tmp
    _ = config.env.s3dir_config
    _ = config.env.s3dir_docs

    # name.py
    _ = config.env.status_tracking_dynamodb_table_name
    _ = config.env.textract_sns_topic_name
    _ = config.env.textract_sns_topic_arn
    _ = config.env.textract_iam_role_name
    _ = config.env.textract_iam_role_arn

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
    _ = config.env.lbd_landing_to_raw
    _ = config.env.lbd_raw_to_tt
    _ = config.env.lbd_tt_to_text

    # name.py
    _ = config.env.cloudformation_stack_name


if __name__ == "__main__":
    from aws_idp_data_store.tests import run_cov_test

    run_cov_test(__file__, "aws_idp_data_store.config", preview=False)
