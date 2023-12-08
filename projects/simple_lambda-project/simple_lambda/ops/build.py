# -*- coding: utf-8 -*-

"""
Build artifacts related automation.
"""

import typing as T
from pathlib import Path

import aws_lambda_layer.api as aws_lambda_layer
import aws_ops_alpha.api as aws_ops_alpha

import aws_ops_alpha.workflow.simple_python.api as simple_python_ops
import aws_ops_alpha.workflow.simple_lambda.api as simple_lambda_ops

from ..config.init import config
from .._api import (
    runtime,
    git_repo,
    EnvEnum,
    detect_current_env,
    boto_ses_factory,
    bsm,
    logger,
    pyproject_ops,
)

from .pyproject import pyproject_ops

if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path

# Emoji = aws_ops_alpha.Emoji


def pip_install():
    simple_python_ops.pip_install(pyproject_ops=pyproject_ops)


def pip_install_dev():
    simple_python_ops.pip_install_dev(pyproject_ops=pyproject_ops)


def pip_install_test():
    simple_python_ops.pip_install_test(pyproject_ops=pyproject_ops)


def pip_install_doc():
    simple_python_ops.pip_install_doc(pyproject_ops=pyproject_ops)


def pip_install_automation():
    simple_python_ops.pip_install_automation(pyproject_ops=pyproject_ops)


def pip_install_all():
    simple_python_ops.pip_install_all(pyproject_ops=pyproject_ops)


def pip_install_all_in_ci():
    simple_python_ops.pip_install_all_in_ci(pyproject_ops=pyproject_ops)


def poetry_lock():
    simple_python_ops.poetry_lock(pyproject_ops=pyproject_ops)


def poetry_export():
    simple_python_ops.poetry_export(pyproject_ops=pyproject_ops)


def run_unit_test(check: bool = True):
    simple_python_ops.run_unit_test(
        git_branch_name=git_repo.git_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        check=check,
    )


def run_cov_test(check: bool = True):
    simple_python_ops.run_cov_test(
        git_branch_name=git_repo.git_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        check=check,
    )


def view_cov():
    simple_python_ops.view_cov(
        pyproject_ops=pyproject_ops,
    )


def build_doc(check: bool = True):
    simple_python_ops.build_doc(
        git_branch_name=git_repo.git_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        check=check,
    )


def view_doc():
    simple_python_ops.view_doc(
        pyproject_ops=pyproject_ops,
    )


def deploy_versioned_doc(check: bool = True):
    simple_python_ops.deploy_versioned_doc(
        git_branch_name=git_repo.git_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        bsm_devops=boto_ses_factory.bsm_devops,
        bucket=config.env.s3_bucket_doc,
        check=check,
    )


def deploy_latest_doc(check: bool = True):
    simple_python_ops.deploy_latest_doc(
        git_branch_name=git_repo.git_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        bsm_devops=boto_ses_factory.bsm_devops,
        bucket=config.env.s3_bucket_doc,
        check=check,
    )


def view_latest_doc():
    simple_python_ops.view_latest_doc(
        pyproject_ops=pyproject_ops,
        bucket=config.env.s3_bucket_doc,
    )


def build_lambda_source(
    verbose: bool = True,
):
    return aws_ops_alpha.aws_lambda_helpers.build_lambda_source(
        pyproject_ops=pyproject_ops,
        verbose=verbose,
    )


def publish_lambda_layer(
    check: bool = True,
):
    return simple_lambda_ops.publish_lambda_layer(
        git_branch_name=git_repo.git_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        bsm_devops=boto_ses_factory.bsm_devops,
        workload_bsm_list=boto_ses_factory.workload_bsm_list,
        pyproject_ops=pyproject_ops,
        layer_name=config.env.lambda_layer_name,
        s3dir_lambda=config.env.s3dir_lambda,
        tags=config.env.devops_aws_tags,
        check=check,
    )


def publish_lambda_version(
    check: bool = True,
):
    env_name = detect_current_env()
    return simple_lambda_ops.publish_lambda_version(
        git_branch_name=git_repo.git_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        bsm_workload=boto_ses_factory.get_env_bsm(env_name),
        lbd_func_name_list=[
            lambda_function.name
            for lambda_function in config.env.lambda_functions.values()
        ],
        check=check,
    )
