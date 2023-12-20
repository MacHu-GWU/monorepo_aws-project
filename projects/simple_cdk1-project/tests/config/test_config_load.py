# -*- coding: utf-8 -*-

from simple_cdk1.config.api import config


def test():
    # main.py
    _ = config
    # from rich import print as rprint
    # rprint(config)
    _ = config.env

    # app.py
    _ = config.env.s3uri_data

    _ = config.env.s3dir_data
    _ = config.env.env_vars
    _ = config.env.devops_aws_tags
    _ = config.env.workload_aws_tags

    # deploy.py
    _ = config.env.s3uri_artifacts
    _ = config.env.s3uri_docs

    _ = config.env.s3dir_artifacts
    _ = config.env.s3dir_env_artifacts
    _ = config.env.s3dir_tmp
    _ = config.env.s3dir_config
    _ = config.env.s3dir_docs

    # name.py
    _ = config.env.cloudformation_stack_name


if __name__ == "__main__":
    from simple_cdk1.tests import run_cov_test

    run_cov_test(__file__, "simple_cdk1.config", preview=False)
