# -*- coding: utf-8 -*-

"""
Developer note:

    every function in the ``step.py`` module should have visualized logging.
"""

# --- standard library
import typing as T
import subprocess
from pathlib import Path

# --- third party library (include vendor)
import aws_console_url.api as aws_console_url
import tt4human.api as tt4human
from versioned.api import Artifact
from aws_glue_artifact.api import GluePythonLibArtifact, GlueETLScriptArtifact
from ...vendor.emoji import Emoji

# --- modules from this project
from ...logger import logger
from ...aws_helpers import aws_cdk_helpers, aws_glue_helpers
from ...rule_set import should_we_do_it

# --- modules from this submodule
from .simple_glue_truth_table import StepEnum, truth_table

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager


@logger.start_and_end(
    msg="Install AWS glue library",
    start_emoji=Emoji.install,
    error_emoji=f"{Emoji.failed} {Emoji.install}",
    end_emoji=f"{Emoji.succeeded} {Emoji.install}",
    pipe=Emoji.install,
)
def pip_install_awsglue(
    pyproject_ops: "pyops.PyProjectOps",
):  # pragma: no cover
    args = [
        f"{pyproject_ops.path_venv_bin_pip}",
        "install",
        # make sure your glue version align with the config.env_name.glue_jobs.job_name.glue_version
        "git+https://github.com/awslabs/aws-glue-libs.git@v4.0",
    ]
    subprocess.run(args)


@logger.start_and_end(
    msg="Build Glue Extra Python Files Artifact",
    start_emoji=f"{Emoji.build} {Emoji.python}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.python}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.python}",
    pipe=Emoji.python,
)
def build_glue_extra_py_files_artifact(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    glue_python_lib_artifact: "GluePythonLibArtifact",
    tags: T.Optional[T.Dict[str, str]] = None,
    check: bool = True,
    step: str = StepEnum.build_glue_artifact_locally.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
) -> T.Optional["Artifact"]:  # pragma: no cover
    """
    Build glue Python library artifacts.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param glue_python_lib_artifact: ``GluePythonLibArtifact`` object.
    :param tags: optional AWS resource tags.
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
    artifact = aws_glue_helpers.build_glue_extra_py_files_artifact(
        bsm_devops=bsm_devops,
        pyproject_ops=pyproject_ops,
        glue_python_lib_artifact=glue_python_lib_artifact,
        tags=tags,
    )
    logger.info(f"preview glue extra py files at: {artifact.s3path.console_url}")
    return artifact


@logger.start_and_end(
    msg="Publish Glue Extra Python Files Artifact Version",
    start_emoji=f"{Emoji.build} {Emoji.python}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.python}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.python}",
    pipe=Emoji.python,
)
def publish_glue_extra_py_files_artifact_version(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    glue_python_lib_artifact: "GluePythonLibArtifact",
    check: bool = True,
    step: str = StepEnum.build_glue_artifact_locally.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
) -> T.Optional["Artifact"]:  # pragma: no cover
    """
    Publish glue Python library artifacts.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param glue_python_lib_artifact: ``GluePythonLibArtifact`` object.
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
    artifact = aws_glue_helpers.publish_glue_extra_py_files_artifact_version(
        bsm_devops=bsm_devops,
        glue_python_lib_artifact=glue_python_lib_artifact,
    )
    logger.info(f"preview glue extra py files at: {artifact.s3path.console_url}")
    return artifact


@logger.start_and_end(
    msg="Build Glue ETL Script Artifact",
    start_emoji=f"{Emoji.build} {Emoji.python}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.python}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.python}",
    pipe=Emoji.python,
)
def build_glue_script_artifact(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    glue_etl_script_artifact_list: T.List["GlueETLScriptArtifact"],
    tags: T.Optional[T.Dict[str, str]] = None,
    check: bool = True,
    step: str = StepEnum.build_glue_artifact_locally.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
) -> T.Optional[T.List["Artifact"]]:  # pragma: no cover
    """
    Build glue ETL script artifacts.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param glue_etl_script_artifact_list: list of ``GlueETLScriptArtifact`` object.
    :param tags: optional AWS resource tags.
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
    artifact_list = aws_glue_helpers.build_glue_script_artifact(
        bsm_devops=bsm_devops,
        pyproject_ops=pyproject_ops,
        glue_etl_script_artifact_list=glue_etl_script_artifact_list,
        tags=tags,
    )
    for artifact in artifact_list:
        logger.info(
            f"preview glue job ETL script artifact {artifact.name!r} at: "
            f"{artifact.s3path.console_url}"
        )
    return artifact_list


@logger.start_and_end(
    msg="Publish Glue ETL Script Artifact Version",
    start_emoji=f"{Emoji.build} {Emoji.python}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.python}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.python}",
    pipe=Emoji.python,
)
def publish_glue_script_artifact_version(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    glue_etl_script_artifact_list: T.List["GlueETLScriptArtifact"],
    check: bool = True,
    step: str = StepEnum.build_glue_artifact_locally.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Publish glue ETL script artifacts.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param bsm_devops: the devops AWS Account ``BotoSesManager`` object.
    :param glue_etl_script_artifact_list: list of ``GlueETLScriptArtifact`` object.
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
    artifact_list = aws_glue_helpers.publish_glue_script_artifact_version(
        bsm_devops=bsm_devops,
        glue_etl_script_artifact_list=glue_etl_script_artifact_list,
    )
    for artifact in artifact_list:
        logger.info(
            f"preview glue job ETL script artifact {artifact.name!r} at: "
            f"{artifact.s3path.console_url}"
        )
    return artifact_list


@logger.start_and_end(
    msg="Run Glue Test",
    start_emoji=Emoji.test,
    error_emoji=f"{Emoji.failed} {Emoji.test}",
    end_emoji=f"{Emoji.succeeded} {Emoji.test}",
    pipe=Emoji.test,
)
def run_glue_unit_test(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    check: bool = True,
    step: str = StepEnum.run_integration_test.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Run Glue unit test.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.
    """
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
    aws_glue_helpers.run_glue_unit_test(pyproject_ops)


@logger.start_and_end(
    msg="Run Glue Integration Test in {env_name}",
    start_emoji=Emoji.test,
    error_emoji=f"{Emoji.failed} {Emoji.test}",
    end_emoji=f"{Emoji.succeeded} {Emoji.test}",
    pipe=Emoji.test,
)
def run_glue_int_test(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    pyproject_ops: "pyops.PyProjectOps",
    check: bool = True,
    step: str = StepEnum.run_integration_test.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
):  # pragma: no cover
    """
    Run Glue integration test.

    :param semantic_branch_name: semantic branch name for conditional step test.
    :param runtime_name: runtime name for conditional step test.
    :param env_name: env name, will be used for conditional step test.
    :param pyproject_ops: ``PyProjectOps`` object.
    :param check: whether to check if we should run this step.
    :param step: step name for conditional step test.
    :param truth_table: truth table for conditional step test.
    :param url: print the Google sheet url when conditional step test failed.
    """
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
    aws_glue_helpers.run_glue_int_test(pyproject_ops)


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
        # build_lambda_source(pyproject_ops=pyproject_ops)
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
        # build_lambda_source(pyproject_ops=pyproject_ops)
        aws_cdk_helpers.cdk_destroy(
            bsm_devops=bsm_devops,
            bsm_workload=bsm_workload,
            dir_cdk=dir_cdk,
            env_name=env_name,
            skip_prompt=skip_prompt,
        )
