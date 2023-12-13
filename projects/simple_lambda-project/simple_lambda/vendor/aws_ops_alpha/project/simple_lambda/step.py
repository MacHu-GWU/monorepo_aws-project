# -*- coding: utf-8 -*-

"""
Developer note:

1. every function in the ``workflow.py`` module should have visualized logging.

"""

# standard library
import typing as T
import time
from pathlib import Path

# third party library (include vendor)
import aws_console_url.api as aws_console_url
from ...vendor.emoji import Emoji
from ...vendor.aws_lambda_version_and_alias import publish_version
from ...vendor import semantic_branch as sem_branch

# modules from this project
from ...logger import logger
from ...aws_helpers import aws_cdk_helpers, aws_lambda_helpers
from ...runtime import Runtime
from ...environment import BaseEnvNameEnum
from ...config.api import BaseConfig, BaseEnv

# modules from this submodule
from .constants import StepEnum, GitBranchNameEnum
from .rule import RuleSet, rule_set as default_rule_set

# type hint
if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path


semantic_branch_rules = {
    GitBranchNameEnum.main: ["main", "master"],
    GitBranchNameEnum.feature: ["feature", "feat"],
    GitBranchNameEnum.fix: ["fix"],
    GitBranchNameEnum.doc: ["doc"],
    GitBranchNameEnum.layer: ["layer"],
    GitBranchNameEnum.app: ["app"],
    GitBranchNameEnum.release: ["release", "rls"],
    GitBranchNameEnum.cleanup: ["cleanup", "clean"],
}

semantic_branch_rule = sem_branch.SemanticBranchRule(
    rules=semantic_branch_rules,
)


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
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    bsm_devops: "BotoSesManager",
    workload_bsm_list: T.List["BotoSesManager"],
    pyproject_ops: "pyops.PyProjectOps",
    layer_name: str,
    s3dir_lambda: "S3Path",
    tags: T.Dict[str, str],
    check=True,
    rule_set: RuleSet = default_rule_set,
):  # pragma: no cover
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.PUBLISH_LAMBDA_LAYER,
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

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
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    bsm_workload: "BotoSesManager",
    lbd_func_name_list: T.List[str],
    check=True,
    rule_set: RuleSet = default_rule_set,
):  # pragma: no cover
    """
    Publish a new lambda version from latest.
    """
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.PUBLISH_NEW_LAMBDA_VERSION,
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
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
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    bsm_workload: "BotoSesManager",
    lbd_func_name_list: T.List[str],
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
    check: bool = True,
    rule_set: RuleSet = default_rule_set,
):  # pragma: no cover
    logger.info(f"deploy app to {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {url}")

    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.DEPLOY_LAMBDA_APP_VIA_CDK,
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    with logger.nested():
        build_lambda_source(pyproject_ops=pyproject_ops)
        aws_cdk_helpers.cdk_deploy(
            bsm_workload=bsm_workload,
            dir_cdk=dir_cdk,
            env_name=env_name,
            skip_prompt=skip_prompt,
        )
        publish_lambda_version(
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
            bsm_workload=bsm_workload,
            lbd_func_name_list=lbd_func_name_list,
            check=check,
            rule_set=rule_set,
        )


@logger.start_and_end(
    msg="Delete App",
    start_emoji=f"{Emoji.delete}",
    error_emoji=f"{Emoji.failed} {Emoji.delete}",
    end_emoji=f"{Emoji.succeeded} {Emoji.delete}",
    pipe=Emoji.delete,
)
def delete_app(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    bsm_workload: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
    skip_prompt: bool = False,
    check: bool = True,
    rule_set: RuleSet = default_rule_set,
):  # pragma: no cover
    logger.info(f"delete app from {env_name!r} env ...")
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_workload)
    url = aws_console.cloudformation.filter_stack(name=stack_name)
    logger.info(f"preview cloudformation stack: {url}")

    if check:
        _mapper = {
            EnvNameEnum.devops.value: StepEnum.DELETE_LAMBDA_APP_IN_SBX.value,
            EnvNameEnum.sbx.value: StepEnum.DELETE_LAMBDA_APP_IN_SBX.value,
            EnvNameEnum.tst.value: StepEnum.DELETE_LAMBDA_APP_IN_TST.value,
            EnvNameEnum.stg.value: StepEnum.DELETE_LAMBDA_APP_IN_STG.value,
            EnvNameEnum.prd.value: StepEnum.DELETE_LAMBDA_APP_IN_PRD.value,
        }

        flag = rule_set.should_we_do_it(
            step=_mapper[env_name],
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    with logger.nested():
        aws_cdk_helpers.cdk_destroy(
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
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    wait: bool = False,
    check: bool = True,
    rule_set: RuleSet = default_rule_set,
):  # pragma: no cover
    logger.info(f"Run integration test in {env_name!r} env...")
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.RUN_INTEGRATION_TEST,
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    # you may want to wait a few seconds for the CDK deployment taking effect
    # you should do this in CI environment if you run integration test
    # right after ``cdk deploy``
    if wait:
        time.sleep(5)
    pyproject_ops.run_int_test()


@logger.emoji_block(
    msg="Create Config Snapshot",
    emoji=Emoji.config,
)
def create_config_snapshot(
    git_branch_name: str,
    env_name: str,
    runtime_name: str,
    runtime: Runtime,
    bsm_devops: "BotoSesManager",
    env_name_enum_class: T.Union[BaseEnvNameEnum, T.Type[BaseEnvNameEnum]],
    env_class: T.Type[BaseEnv],
    config_class: T.Type[BaseConfig],
    version: str,
    path_config_json: T.Optional[Path] = None,
    path_config_secret_json: T.Optional[Path] = None,
    check: bool = True,
    rule_set: RuleSet = default_rule_set,
):  # pragma: no cover
    logger.info(f"Create Config Snapshot in {env_name!r} env...")
    if check:
        flag = rule_set.should_we_do_it(
            step=StepEnum.CREATE_CONFIG_SNAPSHOT,
            git_branch_name=git_branch_name,
            env_name=env_name,
            runtime_name=runtime_name,
        )
        if flag is False:
            return

    s3path = config_class.smart_backup(
        runtime=runtime,
        bsm_devops=bsm_devops,
        env_name_enum_class=env_name_enum_class,
        env_class=env_class,
        version=version,
        path_config_json=path_config_json,
        path_config_secret_json=path_config_secret_json,
    )

    logger.info(f"config snapshot is saved to {s3path.uri}")
    logger.info(f"preview it at: {s3path.console_url}")
