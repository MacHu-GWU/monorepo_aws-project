# -*- coding: utf-8 -*-

"""
Build artifacts related automation.
"""

# standard library
import typing as T

# third party library (include vendor)
import simple_lambda.vendor.aws_ops_alpha.api as aws_ops_alpha

# modules from this project
from .config.load import config
from ._api import (
    paths,
    runtime,
    git_repo,
    EnvNameEnum,
    detect_current_env,
    boto_ses_factory,
    bsm,
    logger,
    pyproject_ops,
)
from .pyproject import pyproject_ops

# type hint
if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path

# Emoji = aws_ops_alpha.Emoji
simple_python_project = aws_ops_alpha.simple_python_project
simple_lambda_project = aws_ops_alpha.simple_lambda_project


def pip_install():
    simple_python_project.pip_install(pyproject_ops=pyproject_ops)


def pip_install_dev():
    simple_python_project.pip_install_dev(pyproject_ops=pyproject_ops)


def pip_install_test():
    simple_python_project.pip_install_test(pyproject_ops=pyproject_ops)


def pip_install_doc():
    simple_python_project.pip_install_doc(pyproject_ops=pyproject_ops)


def pip_install_automation():
    simple_python_project.pip_install_automation(pyproject_ops=pyproject_ops)


def pip_install_all():
    simple_python_project.pip_install_all(pyproject_ops=pyproject_ops)


def pip_install_all_in_ci():
    simple_python_project.pip_install_all_in_ci(pyproject_ops=pyproject_ops)


def poetry_lock():
    simple_python_project.poetry_lock(pyproject_ops=pyproject_ops)


def poetry_export():
    simple_python_project.poetry_export(pyproject_ops=pyproject_ops)


def run_unit_test(check: bool = True):
    simple_python_project.run_unit_test(
        git_branch_name=git_repo.semantic_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        check=check,
        rule_set=simple_lambda_project.rule_set,
    )


def run_cov_test(check: bool = True):
    simple_python_project.run_cov_test(
        git_branch_name=git_repo.semantic_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        check=check,
        rule_set=simple_lambda_project.rule_set,
    )


def view_cov():
    simple_python_project.view_cov(
        pyproject_ops=pyproject_ops,
    )


def build_doc(check: bool = True):
    simple_python_project.build_doc(
        git_branch_name=git_repo.semantic_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        check=check,
        rule_set=simple_lambda_project.rule_set,
    )


def view_doc():
    simple_python_project.view_doc(
        pyproject_ops=pyproject_ops,
    )


def deploy_versioned_doc(check: bool = True):
    simple_python_project.deploy_versioned_doc(
        git_branch_name=git_repo.semantic_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        bsm_devops=boto_ses_factory.bsm_devops,
        bucket=config.env.s3bucket_docs,
        check=check,
        rule_set=simple_lambda_project.rule_set,
    )


def deploy_latest_doc(check: bool = True):
    simple_python_project.deploy_latest_doc(
        git_branch_name=git_repo.semantic_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        bsm_devops=boto_ses_factory.bsm_devops,
        bucket=config.env.s3bucket_docs,
        check=check,
        rule_set=simple_lambda_project.rule_set,
    )


def view_latest_doc():
    simple_python_project.view_latest_doc(
        pyproject_ops=pyproject_ops,
        bucket=config.env.s3bucket_docs,
    )


def build_lambda_source(
    verbose: bool = False,
):
    return simple_lambda_project.build_lambda_source(
        pyproject_ops=pyproject_ops,
        verbose=verbose,
    )


def publish_lambda_layer(
    check: bool = True,
):
    return simple_lambda_project.publish_lambda_layer(
        git_branch_name=git_repo.semantic_branch_name,
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


def deploy_app(
    check: bool = True,
):
    env_name = detect_current_env()
    if runtime.is_local:
        skip_prompt = False
    else:
        skip_prompt = True
    return simple_lambda_project.deploy_app(
        git_branch_name=git_repo.semantic_branch_name,
        env_name=env_name,
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        bsm_workload=boto_ses_factory.get_env_bsm(env_name),
        lbd_func_name_list=config.env.lambda_function_name_list,
        dir_cdk=paths.dir_cdk,
        stack_name=config.env.cloudformation_stack_name,
        # skip_prompt=skip_prompt,
        skip_prompt=True,
        check=check,
    )


def delete_app(
    check: bool = True,
):
    env_name = detect_current_env()
    if runtime.is_local:
        skip_prompt = False
    else:
        skip_prompt = True
    return simple_lambda_project.delete_app(
        git_branch_name=git_repo.semantic_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        bsm_workload=boto_ses_factory.get_env_bsm(env_name),
        dir_cdk=paths.dir_cdk,
        stack_name=config.env.cloudformation_stack_name,
        skip_prompt=skip_prompt,
        check=check,
    )


def publish_lambda_version(
    check: bool = True,
):
    env_name = detect_current_env()
    return simple_lambda_project.publish_lambda_version(
        git_branch_name=git_repo.semantic_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        bsm_workload=boto_ses_factory.get_env_bsm(env_name),
        lbd_func_name_list=config.env.lambda_function_name_list,
        check=check,
    )


def run_int_test(check: bool = True):
    if runtime.is_local:
        wait = False
    else:
        wait = True
    simple_lambda_project.run_int_test(
        git_branch_name=git_repo.semantic_branch_name,
        env_name=detect_current_env(),
        runtime_name=runtime.local_or_ci,
        pyproject_ops=pyproject_ops,
        wait=wait,
        check=check,
    )
