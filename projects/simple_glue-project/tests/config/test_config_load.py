# -*- coding: utf-8 -*-

from simple_glue.boto_ses import boto_ses_factory
from simple_glue.config.api import config


def test():
    # main.py
    _ = config

    _ = config.env

    # app.py
    _ = config.env.s3uri_data

    _ = config.env.s3dir_data
    _ = config.env.s3dir_source
    _ = config.env.s3dir_target
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

    # glue_deploy.py
    _ = config.env.s3dir_glue_artifacts
    _ = config.env.glue_extra_py_files_artifact_name
    _ = config.env.get_glue_extra_py_files_artifact()
    _ = config.env.glue_extra_py_files_artifact_name

    # lbd_func.py
    _ = config.env.glue_jobs
    _ = config.env.glue_job_name_list
    _ = config.env.glue_job_list
    for shortname, glue_job in config.env.glue_jobs.items():
        _ = glue_job.env
        _ = glue_job.short_name
        _ = glue_job.glue_version
        _ = glue_job.worker_type
        _ = glue_job.number_of_workers
        _ = glue_job.max_concurrent_runs
        _ = glue_job.max_retries
        _ = glue_job.timeout
        _ = glue_job.lib_live_version
        _ = glue_job.script_live_version

        _ = glue_job.name
        _ = glue_job.artifact_name
        _ = glue_job.short_name_slug
        _ = glue_job.short_name_snake
        _ = glue_job.short_name_camel
        _ = glue_job.target_lib_live_version
        _ = glue_job.target_script_live_version
        _ = glue_job.immutable_artifact_name
        _ = glue_job.mutable_artifact_name
        _ = glue_job.path_glue_script
        _ = glue_job.get_glue_script_content
        _ = glue_job.get_immutable_glue_etl_script_artifact
        _ = glue_job.get_mutable_glue_etl_script_artifact

    _ = config.env.glue_unnest

    # name.py
    _ = config.env.cloudformation_stack_name


if __name__ == "__main__":
    from simple_glue.tests import run_cov_test

    run_cov_test(__file__, "simple_glue.config", preview=False)
