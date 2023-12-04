# -*- coding: utf-8 -*-

"""
Build artifacts related automation.
"""

import typing as T
from aws_lambda_layer.api import (
    build_source_artifacts,
    publish_source_artifacts,
    SourceArtifactsDeployment,
    deploy_layer,
    grant_layer_permission,
)
import aws_ops_alpha.api as aws_ops_alpha

from .pyproject import pyproject_ops
from .logger import logger
from .emoji import Emoji
from .git import GIT_BRANCH_NAME, IS_LAYER_BRANCH
from .runtime import IS_CI


if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path


def build_lambda_source_only(
    verbose: bool = True,
):
    path_lambda_function = pyproject_ops.dir_lambda_app.joinpath("lambda_function.py")
    source_sha256, path_source_zip = build_source_artifacts(
        path_setup_py_or_pyproject_toml=pyproject_ops.path_pyproject_toml,
        package_name=pyproject_ops.package_name,
        path_lambda_function=path_lambda_function,
        dir_build=pyproject_ops.dir_build_lambda,
        use_pathlib=True,
        verbose=verbose,
    )
    return source_sha256, path_source_zip


def _build_lambda_source(
    bsm: "BotoSesManager",
    s3dir_lambda: "S3Path",
    tags: T.Dict[str, str],
    verbose: bool = True,
) -> SourceArtifactsDeployment:
    path_lambda_function = pyproject_ops.dir_lambda_app.joinpath("lambda_function.py")
    return publish_source_artifacts(
        bsm=bsm,
        path_setup_py_or_pyproject_toml=pyproject_ops.path_pyproject_toml,
        package_name=pyproject_ops.package_name,
        path_lambda_function=path_lambda_function,
        version=pyproject_ops.package_version,
        dir_build=pyproject_ops.dir_build_lambda,
        s3dir_lambda=s3dir_lambda.to_dir(),
        verbose=verbose,
        tags=tags,
        use_pathlib=True,
    )


@logger.start_and_end(
    msg="Build Lambda Source Artifacts",
    start_emoji=f"{Emoji.build} {Emoji.awslambda}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.awslambda}",
)
def build_lambda_source(
    bsm: "BotoSesManager",
    s3dir_lambda: "S3Path",
    tags: T.Dict[str, str],
    verbose: bool = False,
):
    source_artifacts_deployment = _build_lambda_source(
        bsm=bsm,
        s3dir_lambda=s3dir_lambda,
        tags=tags,
        verbose=verbose,
    )
    path = source_artifacts_deployment.path_source_zip
    logger.info(f"review source artifacts at local: {path}")
    console_url = source_artifacts_deployment.s3path_source_zip.console_url
    logger.info(f"review source artifacts in s3: {console_url}")


def _build_lambda_layer(
    bsm: "BotoSesManager",
    layer_name: str,
    s3dir_lambda: "S3Path",
    tags: T.Dict[str, str],
):
    return deploy_layer(
        bsm=bsm,
        layer_name=layer_name,
        python_versions=[
            f"python{pyproject_ops.python_version}",
        ],
        path_requirements=pyproject_ops.path_requirements,
        dir_build=pyproject_ops.dir_build_lambda,
        s3dir_lambda=s3dir_lambda,
        bin_pip=pyproject_ops.path_venv_bin_pip,
        quiet=True,
        tags=tags,
    )


@logger.start_and_end(
    msg="Build Lambda Layer Artifacts",
    start_emoji=f"{Emoji.build} {Emoji.awslambda}",
    error_emoji=f"{Emoji.failed} {Emoji.build} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.build} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def build_lambda_layer(
    bsm_devops: "BotoSesManager",
    workload_bsm_list: T.List["BotoSesManager"],
    layer_name: str,
    s3dir_lambda: "S3Path",
    tags: T.Dict[str, str],
    check=True,
):
    if check:
        if (
            aws_ops_alpha.simple_lambda.do_we_deploy_lambda_layer(
                is_ci_runtime=IS_CI,
                branch_name=GIT_BRANCH_NAME,
                is_layer_branch=IS_LAYER_BRANCH,
            )
            is False
        ):
            return

    layer_deployment = _build_lambda_layer(
        bsm=bsm_devops,
        layer_name=layer_name,
        s3dir_lambda=s3dir_lambda,
        tags=tags,
    )
    if layer_deployment is None:
        logger.info(
            f"{Emoji.red_circle} don't publish layer, "
            f"the current requirements.txt is the same as the one "
            f"of the latest lambda layer."
        )
    else:
        logger.info(f"published a new layer version: {layer_deployment.layer_version}")
        logger.info(f"published layer arn: {layer_deployment.layer_version_arn}")
        layer_console_url = (
            f"https://{bsm_devops.aws_region}.console.aws.amazon.com/lambda"
            f"/home?region={bsm_devops.aws_region}#"
            f"/layers?fo=and&o0=%3A&v0={layer_name}"
        )
        logger.info(f"preview deployed layer at {layer_console_url}")
        console_url = layer_deployment.s3path_layer_zip.console_url
        logger.info(f"preview layer.zip at {console_url}")
        console_url = layer_deployment.s3path_layer_requirements_txt.console_url
        logger.info(f"preview requirements.txt at {console_url}")

        for bsm_workload in workload_bsm_list:
            grant_layer_permission(
                bsm=bsm_devops,
                layer_name=layer_name,
                version_number=layer_deployment.layer_version,
                principal=bsm_workload.aws_account_id,
            )
