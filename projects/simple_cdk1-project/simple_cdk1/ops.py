# -*- coding: utf-8 -*-

"""
Build artifacts related automation.
"""

# standard library

# third party library (include vendor)
from simple_cdk1.vendor.import_agent import aws_ops_alpha

# modules from this project
from ._version import __version__
from .config.api import Config, Env, config
from ._api import (
    paths,
    runtime,
    git_repo,
    EnvNameEnum,
    detect_current_env,
    boto_ses_factory,
)
from .pyproject import pyproject_ops


# Emoji = aws_ops_alpha.Emoji
simple_python_project = aws_ops_alpha.simple_python_project
simple_config_project = aws_ops_alpha.simple_config_project
simple_cdk_project = aws_ops_alpha.simple_cdk_project


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


def deploy_config(check: bool = True):
    simple_config_project.deploy_config(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        config=config,
        bsm={
            "all": boto_ses_factory.bsm_devops,
            EnvNameEnum.devops.value: boto_ses_factory.bsm_devops,
            EnvNameEnum.sbx.value: boto_ses_factory.bsm_sbx,
            EnvNameEnum.tst.value: boto_ses_factory.bsm_tst,
            EnvNameEnum.prd.value: boto_ses_factory.bsm_prd,
        },
        parameter_with_encryption=True,
        check=check,
        step=simple_cdk_project.StepEnum.deploy_config.value,
        truth_table=simple_cdk_project.truth_table,
        url=simple_cdk_project.google_sheet_url,
    )


def run_unit_test(check: bool = True):
    simple_python_project.run_unit_test(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        pyproject_ops=pyproject_ops,
        check=check,
        step=simple_cdk_project.StepEnum.run_code_coverage_test.value,
        truth_table=simple_cdk_project.truth_table,
        url=simple_cdk_project.google_sheet_url,
    )


def run_cov_test(check: bool = True):
    simple_python_project.run_cov_test(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        pyproject_ops=pyproject_ops,
        check=check,
        step=simple_cdk_project.StepEnum.run_code_coverage_test.value,
        truth_table=simple_cdk_project.truth_table,
        url=simple_cdk_project.google_sheet_url,
    )


def view_cov():
    simple_python_project.view_cov(
        pyproject_ops=pyproject_ops,
    )


def build_doc(check: bool = True):
    if runtime.is_local_runtime_group:
        check = False
    simple_python_project.build_doc(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        pyproject_ops=pyproject_ops,
        check=check,
        step=simple_cdk_project.StepEnum.build_documentation.value,
        truth_table=simple_cdk_project.truth_table,
        url=simple_cdk_project.google_sheet_url,
    )


def view_doc():
    simple_python_project.view_doc(
        pyproject_ops=pyproject_ops,
    )


def deploy_versioned_doc(check: bool = True):
    if runtime.is_local_runtime_group:
        check = False
    simple_python_project.deploy_versioned_doc(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        pyproject_ops=pyproject_ops,
        bsm_devops=boto_ses_factory.bsm_devops,
        bucket=config.env.s3bucket_docs,
        check=check,
        step=simple_cdk_project.StepEnum.update_documentation.value,
        truth_table=simple_cdk_project.truth_table,
        url=simple_cdk_project.google_sheet_url,
    )


def deploy_latest_doc(check: bool = True):
    if runtime.is_local_runtime_group:
        check = False
    simple_python_project.deploy_latest_doc(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        pyproject_ops=pyproject_ops,
        bsm_devops=boto_ses_factory.bsm_devops,
        bucket=config.env.s3bucket_docs,
        check=check,
        step=simple_cdk_project.StepEnum.update_documentation.value,
        truth_table=simple_cdk_project.truth_table,
        url=simple_cdk_project.google_sheet_url,
    )


def view_latest_doc():
    simple_python_project.view_latest_doc(
        pyproject_ops=pyproject_ops,
        bucket=config.env.s3bucket_docs,
    )


def deploy_app(
    check: bool = True,
):
    boto_ses_factory.print_who_am_i()
    env_name = detect_current_env()
    if runtime.is_local:
        skip_prompt = False
    else:
        skip_prompt = True
    skip_prompt = True  # uncomment this if you always want to skip prompt
    return simple_cdk_project.cdk_deploy(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        bsm_workload=boto_ses_factory.get_env_bsm(env_name),
        dir_cdk=paths.dir_cdk,
        stack_name=config.env.cloudformation_stack_name,
        skip_prompt=skip_prompt,
        check=check,
        step=simple_cdk_project.StepEnum.deploy_cdk_stack.value,
        truth_table=simple_cdk_project.truth_table,
        url=simple_cdk_project.google_sheet_url,
    )


def delete_app(
    check: bool = True,
):
    boto_ses_factory.print_who_am_i()
    env_name = detect_current_env()
    if runtime.is_local:
        skip_prompt = False
    else:
        skip_prompt = True
    skip_prompt = True # uncomment this if you always want to skip prompt
    return simple_cdk_project.cdk_destroy(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        bsm_workload=boto_ses_factory.get_env_bsm(env_name),
        dir_cdk=paths.dir_cdk,
        stack_name=config.env.cloudformation_stack_name,
        skip_prompt=skip_prompt,
        check=check,
        step=simple_cdk_project.StepEnum.delete_cdk_stack.value,
        truth_table=simple_cdk_project.truth_table,
        url=simple_cdk_project.google_sheet_url,
    )


def run_int_test(check: bool = True):
    simple_python_project.run_int_test(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        pyproject_ops=pyproject_ops,
        check=check,
        step=simple_cdk_project.StepEnum.run_integration_test.value,
        truth_table=simple_cdk_project.truth_table,
        url=simple_cdk_project.google_sheet_url,
    )


def create_config_snapshot(check: bool = True):
    simple_config_project.create_config_snapshot(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        runtime=runtime,
        bsm_devops=boto_ses_factory.bsm_devops,
        env_name_enum_class=EnvNameEnum,
        env_class=Env,
        config_class=Config,
        version=__version__,
        path_config_json=paths.path_config_json,
        path_config_secret_json=paths.path_config_secret_json,
        check=check,
        step=simple_cdk_project.StepEnum.create_artifact_snapshot.value,
        truth_table=simple_cdk_project.truth_table,
        url=simple_cdk_project.google_sheet_url,
    )


def delete_config(check: bool = True):
    simple_config_project.delete_config(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        config=config,
        bsm={
            "all": boto_ses_factory.bsm_devops,
            EnvNameEnum.devops.value: boto_ses_factory.bsm_devops,
            EnvNameEnum.sbx.value: boto_ses_factory.bsm_sbx,
            EnvNameEnum.tst.value: boto_ses_factory.bsm_tst,
            EnvNameEnum.prd.value: boto_ses_factory.bsm_prd,
        },
        use_parameter_store=True,
        check=check,
        step=simple_cdk_project.StepEnum.delete_config.value,
        truth_table=simple_cdk_project.truth_table,
        url=simple_cdk_project.google_sheet_url,
    )
