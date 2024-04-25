# -*- coding: utf-8 -*-

"""
Developer note:

    every function in the ``step.py`` module should have visualized logging.
"""

# --- standard library
import typing as T
import time
import subprocess
from pathlib import Path

# --- third party library (include vendor)
import aws_console_url.api as aws_console_url
import tt4human.api as tt4human
from ...vendor.emoji import Emoji
from ...vendor.aws_lambda_version_and_alias import publish_version

# --- modules from this project
from ...logger import logger
from ...aws_helpers.api import aws_cdk_helpers, aws_lambda_helpers
from ...runtime.api import RunTimeEnum
from ...rule_set import should_we_do_it

# --- modules from this submodule
from .simple_lambda_truth_table import StepEnum, truth_table

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path


@logger.start_and_end(
    msg="Build Lambda Source Artifacts",
    start_emoji=f"{Emoji.build} {Emoji.awslambda}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def build_lambda_source(
    pyproject_ops: "pyops.PyProjectOps",
    verbose: bool = False,
):  # pragma: no cover
    source_sha256, path_source_zip = aws_lambda_helpers.build_lambda_source(
        pyproject_ops=pyproject_ops,
        verbose=verbose,
    )
    logger.info(f"review source artifacts at local: {path_source_zip}")
    logger.info(f"review source artifacts sha256: {source_sha256}")


@logger.start_and_end(
    msg="Build Lambda Layer Artifacts",
    start_emoji=f"{Emoji.build} {Emoji.awslambda}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def publish_lambda_layer(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    workload_bsm_list: T.List["BotoSesManager"],
    pyproject_ops: "pyops.PyProjectOps",
    layer_name: str,
    s3dir_lambda: "S3Path",
    tags: T.Dict[str, str],
    is_arm: bool = False,
    check: bool = True,
    step: str = StepEnum.publish_lambda_layer.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Build layer locally, and upload layer artifacts to S3, then publish lambda layer,
    and grant cross account permission.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param workload_bsm_list: list of all workload AWS Accounts ``BotoSesManager`` objects.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param layer_name: Lambda layer name.
    :param s3dir_lambda: the S3 folder to store all lambda layer version artifacts.
    :param tags: optional AWS resource tags.
    :param is_arm: is True, then build for ARM architecture, otherwise build for x86_64.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.
    """
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return

    if runtime_name == RunTimeEnum.local.name:
        logger.info(f"runtime is local, build layer in docker")
        layer_deployment = aws_lambda_helpers.deploy_layer_using_docker(
            bsm_devops=bsm_devops,
            pyproject_ops=pyproject_ops,
            layer_name=layer_name,
            s3dir_lambda=s3dir_lambda,
            tags=tags,
            is_arm=is_arm,
        )
    else:
        logger.info(f"build lambda layer")
        layer_deployment = aws_lambda_helpers.deploy_layer(
            bsm_devops=bsm_devops,
            pyproject_ops=pyproject_ops,
            layer_name=layer_name,
            s3dir_lambda=s3dir_lambda,
            tags=tags,
        )

    aws_lambda_helpers.explain_layer_deployment(
        bsm_devops=bsm_devops,
        layer_deployment=layer_deployment,
    )

    if layer_deployment is not None:
        logger.info(f"grant layer permission to workload accounts")
        principal_list = aws_lambda_helpers.grant_layer_permission(
            bsm_devops=bsm_devops,
            workload_bsm_list=workload_bsm_list,
            layer_deployment=layer_deployment,
        )
        for principal in principal_list:
            logger.info(f"grant layer permission to {principal}")

    return layer_deployment


@logger.emoji_block(
    msg="Publish new Lambda version",
    emoji=Emoji.awslambda,
)
def publish_lambda_version(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_workload: "BotoSesManager",
    lbd_func_name_list: T.List[str],
    check: bool = True,
    step: str = StepEnum.publish_new_lambda_version.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Publish a new lambda version from latest.

    .. note::

        before 2023-06, AWS CDK doesn't support to manage lambda version and alias
        automatically, so we need to publish new lambda version manually.
        now AWS CDK can automatically roll up version and retain historical versions,
        so we don't need this function anymore. I intentionally keep this function
        in case we need this when not using AWS CDK.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param bsm_workload: the workload AWS Account ``BotoSesManager`` object.
    :param lbd_func_name_list: list of lambda function names.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.
    """
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return

    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    for lbd_func_name in lbd_func_name_list:
        url = aws_console.awslambda.get_function(lbd_func_name)
        logger.info(f"preview lambda function {lbd_func_name!r}: {url}", 1)
        publish_version(lbd_client=bsm_workload.lambda_client, func_name=lbd_func_name)


@logger.start_and_end(
    msg="Deploy App",
    start_emoji=f"{Emoji.deploy}",
    error_emoji=f"{Emoji.failed} {Emoji.deploy}",
    end_emoji=f"{Emoji.succeeded} {Emoji.deploy}",
    pipe=Emoji.deploy,
)
def deploy_app(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    bsm_devops: "BotoSesManager",
    bsm_workload: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
    check: bool = True,
    step: str = StepEnum.deploy_cdk_stack.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Deploy Lambda app using AWS CDK.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param bsm_workload: the workload AWS Account ``BotoSesManager`` object.
    :param dir_cdk: the CDK directory, there should be an app.py and cdk.json file in it.
    :param stack_name: CloudFormation stack name.
    :param skip_prompt: if True, then skip prompt for ``cdk deploy`` command.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.
    """
    logger.info(f"deploy app to {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    console_url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {console_url}")

    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            runtime_name=runtime_name,
            env_name=env_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return

    with logger.nested():
        build_lambda_source(pyproject_ops=pyproject_ops)
        aws_cdk_helpers.cdk_deploy(
            bsm_devops=bsm_devops,
            bsm_workload=bsm_workload,
            dir_cdk=dir_cdk,
            env_name=env_name,
            skip_prompt=skip_prompt,
        )


@logger.start_and_end(
    msg="Delete App",
    start_emoji=f"{Emoji.delete}",
    error_emoji=f"{Emoji.failed} {Emoji.delete}",
    end_emoji=f"{Emoji.succeeded} {Emoji.delete}",
    pipe=Emoji.delete,
)
def delete_app(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    bsm_devops: "BotoSesManager",
    bsm_workload: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
    check: bool = True,
    step: str = StepEnum.delete_cdk_stack.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Delete Lambda app using AWS CDK.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param bsm_workload: the workload AWS Account ``BotoSesManager`` object.
    :param dir_cdk: the CDK directory, there should be an app.py and cdk.json file in it.
    :param stack_name: CloudFormation stack name.
    :param skip_prompt: if True, then skip prompt for ``cdk delete`` command.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.
    """
    logger.info(f"delete app from {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    console_url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {console_url}")

    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return

    with logger.nested():
        build_lambda_source(pyproject_ops=pyproject_ops)
        aws_cdk_helpers.cdk_destroy(
            bsm_devops=bsm_devops,
            bsm_workload=bsm_workload,
            dir_cdk=dir_cdk,
            env_name=env_name,
            skip_prompt=skip_prompt,
        )


@logger.emoji_block(
    msg="Run Integration Test",
    emoji=Emoji.test,
)
def run_int_test(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    wait: bool = False,
    check: bool = True,
    step: str = StepEnum.run_integration_test.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Run integration test.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param wait: wait a few seconds for the CDK deployment taking effect.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.
    """
    logger.info(f"Run integration test in {env_name!r} env...")
    if check:
        flag = should_we_do_it(
            step=step,
            semantic_branch_name=semantic_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
            truth_table=truth_table,
            google_sheet_url=url,
        )
        if flag is False:
            return

    # you may want to wait a few seconds for the CDK deployment taking effect
    # you should do this in CI environment if you run integration test
    # right after ``cdk deploy``
    if wait:
        time.sleep(5)
    pyproject_ops.run_int_test()
