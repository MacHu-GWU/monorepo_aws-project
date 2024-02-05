# -*- coding: utf-8 -*-

"""
This module implements the automation to manage AWS lambda artifacts, versions, etc ...
"""

import typing as T
from pathlib import Path

import aws_lambda_layer.api as aws_lambda_layer
import aws_console_url.api as aws_console_url
from ..vendor.emoji import Emoji

from ..logger import logger


if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path


def build_lambda_source(
    pyproject_ops: "pyops.PyProjectOps",
    verbose: bool = True,
) -> T.Tuple[str, Path]:  # pragma: no cover
    """
    Wrapper of ``aws_lambda_layer.api.build_source_artifacts``.

    Build lambda source artifacts locally and return source code sha256 and zip file path.
    It will NOT upload the artifacts to S3.

    :return: tuple of two items: (source code sha256, zip file path)
    """
    path_lambda_function = pyproject_ops.dir_lambda_app.joinpath("lambda_function.py")
    source_sha256, path_source_zip = aws_lambda_layer.build_source_artifacts(
        path_setup_py_or_pyproject_toml=pyproject_ops.path_pyproject_toml,
        package_name=pyproject_ops.package_name,
        path_lambda_function=path_lambda_function,
        dir_build=pyproject_ops.dir_build_lambda,
        use_pathlib=True,
        verbose=verbose,
    )
    return source_sha256, path_source_zip


def deploy_layer(
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    layer_name: str,
    s3dir_lambda: "S3Path",
    tags: T.Dict[str, str],
) -> T.Optional[aws_lambda_layer.LayerDeployment]:  # pragma: no cover
    """
    Publish lambda layer.

    This function doesn't have any logging, it can make the final function shorter.
    """
    return aws_lambda_layer.deploy_layer(
        bsm=bsm_devops,
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


def grant_layer_permission(
    bsm_devops: "BotoSesManager",
    workload_bsm_list: T.List["BotoSesManager"],
    layer_deployment: aws_lambda_layer.LayerDeployment,
) -> T.List[str]:  # pragma: no cover
    principal_list = list()
    for bsm_workload in workload_bsm_list:
        if (bsm_devops.aws_account_id == bsm_workload.aws_account_id) and (
            bsm_devops.aws_region == bsm_workload.aws_region
        ):
            continue
        aws_lambda_layer.grant_layer_permission(
            bsm=bsm_devops,
            layer_name=layer_deployment.layer_name,
            version_number=layer_deployment.layer_version,
            principal=bsm_workload.aws_account_id,
        )
        principal_list.append(bsm_workload.aws_account_id)
    return principal_list


def explain_layer_deployment(
    bsm_devops: "BotoSesManager",
    layer_deployment: T.Optional[aws_lambda_layer.LayerDeployment],
):  # pragma: no cover
    if layer_deployment is None:
        logger.info(
            f"{Emoji.red_circle} don't publish layer, "
            f"the current requirements.txt is the same as the one "
            f"of the latest lambda layer."
        )
    else:
        aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm_devops)
        logger.info(f"published a new layer version: {layer_deployment.layer_version}")
        logger.info(f"published layer arn: {layer_deployment.layer_version_arn}")
        layer_console_url = aws_console.awslambda.filter_layers(
            layer_deployment.layer_name
        )
        logger.info(f"preview deployed layer at {layer_console_url}")
        console_url = layer_deployment.s3path_layer_zip.console_url
        logger.info(f"preview layer.zip at {console_url}")
        console_url = layer_deployment.s3path_layer_requirements_txt.console_url
        logger.info(f"preview requirements.txt at {console_url}")
