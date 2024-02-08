# -*- coding: utf-8 -*-

"""
Build artifacts related automation.
"""

# standard library
import typing as T

# third party library (include vendor)
import simple_lbd_agw_chalice.vendor.aws_ops_alpha.api as aws_ops_alpha

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
simple_lambda_project = aws_ops_alpha.simple_lambda_project
simple_lbd_agw_chalice_project = aws_ops_alpha.simple_lbd_agw_chalice_project


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
        step=simple_lambda_project.StepEnum.deploy_config.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
    )


def run_unit_test(check: bool = True):
    simple_python_project.run_unit_test(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        pyproject_ops=pyproject_ops,
        check=check,
        step=simple_lambda_project.StepEnum.run_code_coverage_test.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
    )


def run_cov_test(check: bool = True):
    simple_python_project.run_cov_test(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        pyproject_ops=pyproject_ops,
        check=check,
        step=simple_lambda_project.StepEnum.run_code_coverage_test.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
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
        step=simple_lambda_project.StepEnum.build_documentation.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
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
        bucket=config.env.s3dir_docs.bucket,
        prefix=config.env.s3dir_docs.key,
        check=check,
        step=simple_lambda_project.StepEnum.update_documentation.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
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
        bucket=config.env.s3dir_docs.bucket,
        prefix=config.env.s3dir_docs.key,
        check=check,
        step=simple_lambda_project.StepEnum.update_documentation.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
    )


def view_latest_doc():
    simple_python_project.view_latest_doc(
        pyproject_ops=pyproject_ops,
        bucket=config.env.s3dir_docs.bucket,
        prefix=config.env.s3dir_docs.key,
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
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        bsm_devops=boto_ses_factory.bsm_devops,
        workload_bsm_list=boto_ses_factory.workload_bsm_list,
        pyproject_ops=pyproject_ops,
        layer_name=config.env.lambda_layer_name,
        s3dir_lambda=config.env.s3dir_lambda,
        tags=config.env.devops_aws_tags,
        is_arm=False,
        check=check,
        step=simple_lambda_project.StepEnum.publish_lambda_layer.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
    )


def download_deployed_json(
    check: bool = True,
):
    return simple_lbd_agw_chalice_project.download_deployed_json(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        bsm_devops=boto_ses_factory.bsm_devops,
        pyproject_ops=pyproject_ops,
        s3dir_deployed=config.env.s3dir_deployed,
        check=check,
        step=simple_lbd_agw_chalice_project.StepEnum.deploy_chalice_app.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
    )


def upload_deployed_json(
    check: bool = True,
):
    return simple_lbd_agw_chalice_project.upload_deployed_json(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        bsm_devops=boto_ses_factory.bsm_devops,
        pyproject_ops=pyproject_ops,
        s3dir_deployed=config.env.s3dir_deployed,
        source_sha256=None,
        tags=config.env.workload_aws_tags,
        check=check,
        step=simple_lbd_agw_chalice_project.StepEnum.deploy_chalice_app.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
    )


def deploy_stack(
    check: bool = True,
):
    env_name = detect_current_env()
    if runtime.is_local:
        skip_prompt = False
    else:
        skip_prompt = True
    skip_prompt = True  # uncomment this if you always want to skip prompt
    return simple_cdk_project.cdk_deploy(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=env_name,
        bsm_devops=boto_ses_factory.bsm_devops,
        bsm_workload=boto_ses_factory.get_env_bsm(env_name),
        dir_cdk=paths.dir_cdk,
        stack_name=config.env.cloudformation_stack_name,
        skip_prompt=skip_prompt,
        check=check,
        step=simple_lbd_agw_chalice_project.StepEnum.deploy_cdk_stack.value,
        truth_table=simple_lbd_agw_chalice_project.truth_table,
        url=simple_lbd_agw_chalice_project.google_sheet_url,
    )


def delete_stack(
    check: bool = True,
):
    env_name = detect_current_env()
    if runtime.is_local:
        skip_prompt = False
    else:
        skip_prompt = True
    skip_prompt = True  # uncomment this if you always want to skip prompt
    return simple_cdk_project.cdk_destroy(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=env_name,
        bsm_devops=boto_ses_factory.bsm_devops,
        bsm_workload=boto_ses_factory.get_env_bsm(env_name),
        dir_cdk=paths.dir_cdk,
        stack_name=config.env.cloudformation_stack_name,
        skip_prompt=skip_prompt,
        check=check,
        step=simple_lambda_project.StepEnum.delete_cdk_stack.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
    )


def run_chalice_deploy(
    check: bool = True,
):
    env_name = detect_current_env()
    return simple_lbd_agw_chalice_project.run_chalice_deploy(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=env_name,
        chalice_app_name=config.env.chalice_app_name,
        bsm_devops=boto_ses_factory.bsm_devops,
        bsm_workload=boto_ses_factory.get_env_bsm(env_name),
        pyproject_ops=pyproject_ops,
        s3path_deployed_json=config.env.s3dir_deployed / f"{env_name}.json",
        tags=config.env.workload_aws_tags,
        check=check,
        step=simple_lbd_agw_chalice_project.StepEnum.deploy_chalice_app.value,
        truth_table=simple_lbd_agw_chalice_project.truth_table,
        url=simple_lbd_agw_chalice_project.google_sheet_url,
    )


def run_chalice_delete(
    check: bool = True,
):
    env_name = detect_current_env()
    return simple_lbd_agw_chalice_project.run_chalice_delete(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=env_name,
        chalice_app_name=config.env.chalice_app_name,
        bsm_devops=boto_ses_factory.bsm_devops,
        bsm_workload=boto_ses_factory.get_env_bsm(env_name),
        pyproject_ops=pyproject_ops,
        s3path_deployed_json=config.env.s3dir_deployed / f"{env_name}.json",
        tags=config.env.workload_aws_tags,
        check=check,
        step=simple_lbd_agw_chalice_project.StepEnum.delete_chalice_app.value,
        truth_table=simple_lbd_agw_chalice_project.truth_table,
        url=simple_lbd_agw_chalice_project.google_sheet_url,
    )


def publish_lambda_version(
    check: bool = True,
):
    env_name = detect_current_env()
    return simple_lambda_project.publish_lambda_version(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        bsm_workload=boto_ses_factory.get_env_bsm(env_name),
        lbd_func_name_list=config.env.lambda_function_name_list,
        check=check,
        step=simple_lambda_project.StepEnum.publish_new_lambda_version.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
    )


def run_int_test(check: bool = True):
    if runtime.is_local:
        wait = False
    else:
        wait = True
    simple_lambda_project.run_int_test(
        semantic_branch_name=git_repo.semantic_branch_name,
        runtime_name=runtime.current_runtime_group,
        env_name=detect_current_env(),
        pyproject_ops=pyproject_ops,
        wait=wait,
        check=check,
        step=simple_lambda_project.StepEnum.run_integration_test.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
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
        step=simple_lambda_project.StepEnum.create_artifact_snapshot.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
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
        step=simple_lambda_project.StepEnum.delete_config.value,
        truth_table=simple_lambda_project.truth_table,
        url=simple_lambda_project.google_sheet_url,
    )


def show_context_info():
    simple_python_project.show_context_info(
        git_branch_name=git_repo.git_branch_name,
        runtime_name=runtime.current_runtime,
        env_name=detect_current_env(),
        git_commit_id=git_repo.git_commit_id,
        git_commit_message=git_repo.git_commit_message,
    )


def create_important_path_table():
    return aws_ops_alpha.rich_helpers.create_path_table(
        name_and_path_list=[
            ("dir_project_root", pyproject_ops.dir_project_root),
            ("dir_python_lib", pyproject_ops.dir_python_lib),
            ("dir_venv", pyproject_ops.dir_venv),
            ("path_venv_bin_python", pyproject_ops.path_venv_bin_python),
            ("path_config_json", pyproject_ops.path_config_json),
            ("path_secret_config_json", pyproject_ops.path_secret_config_json),
            ("dir_tests", pyproject_ops.dir_tests),
            ("dir_docs", pyproject_ops.dir_sphinx_doc_source),
            ("dir_build_lambda", pyproject_ops.dir_build_lambda),
        ]
    )


def create_important_s3_location_table():
    return aws_ops_alpha.rich_helpers.create_s3path_table(
        name_and_s3path_list=[
            ("s3dir_artifacts", config.env.s3dir_artifacts),
            ("s3dir_docs", config.env.s3dir_docs),
            ("s3dir_data", config.env.s3dir_data),
            ("s3dir_config", config.env.s3dir_config),
            ("s3dir_lambda", config.env.s3dir_lambda),
        ]
    )


def create_important_url_table():
    import aws_console_url.api as aws_console_url

    aws = aws_console_url.AWSConsole.from_bsm(boto_ses_factory.bsm_devops)
    endpoint = config.env.get_api_gateway_endpoint(boto_ses_factory.bsm_devops)
    rest_api_id = config.env.endpoint_to_rest_api_id(endpoint)
    return aws_ops_alpha.rich_helpers.create_url_table(
        name_and_url_list=[
            # fmt: off
            ("parameter store", aws.ssm.filter_parameters(config.parameter_name)),
            ("cloudformation stacks", aws.cloudformation.filter_stack(config.project_name_slug)),
            ("api gateway", aws.apigateway.get_v1_rest_api(rest_api_id)),
            ("lambda functions", aws.awslambda.filter_functions(config.project_name)),
            ("lambda layer", aws.awslambda.filter_layers(config.env.lambda_layer_name)),
            # fmt: on
        ]
    )


def show_project_info():
    from rich.console import Console

    console = Console()
    console.print(create_important_path_table())
    console.print(create_important_s3_location_table())
    console.print(create_important_url_table())
