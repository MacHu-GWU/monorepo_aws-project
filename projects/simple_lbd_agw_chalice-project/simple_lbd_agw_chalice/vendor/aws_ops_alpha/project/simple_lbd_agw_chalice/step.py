# -*- coding: utf-8 -*-

"""
Developer note:

    every function in the ``step.py`` module should have visualized logging.
"""

# --- standard library
import typing as T
import json
from pathlib import Path
from datetime import datetime

# --- third party library (include vendor)
import tt4human.api as tt4human
from ...vendor.emoji import Emoji

# --- modules from this project
from ...logger import logger
from ...aws_helpers import aws_chalice_helpers
from ...rule_set import should_we_do_it

# --- modules from this submodule
from .simple_lbd_agw_chalice_truth_table import StepEnum, truth_table

# --- type hint
if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path


# todo: add concurrency lock mechanism
@logger.start_and_end(
    msg="Download deployed/${{env_name}}.json from S3",
    start_emoji=Emoji.awslambda,
    error_emoji=f"{Emoji.failed} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def download_deployed_json(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    s3dir_deployed: "S3Path",
    check=True,
    step: str = StepEnum.deploy_chalice_app.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
) -> bool:
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
            return False

    s3path_deployed_json = s3dir_deployed / f"{env_name}.json"
    logger.info(
        f"try to download existing deployed {env_name}.json file from "
        f"{s3path_deployed_json.s3_select_console_url}"
    )
    flag = aws_chalice_helpers.download_deployed_json(
        env_name=env_name,
        bsm_devops=bsm_devops,
        pyproject_ops=pyproject_ops,
        s3dir_deployed=s3dir_deployed,
    )
    if flag is False:
        logger.info("no existing deployed json file found, skip download")
    return flag


@logger.start_and_end(
    msg="Upload deployed/$env_name.json to S3",
    start_emoji=Emoji.awslambda,
    error_emoji=f"{Emoji.failed} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def upload_deployed_json(
    semantic_branch_name: str,
    runtime_name: str,
    env_name: str,
    bsm_devops: "BotoSesManager",
    pyproject_ops: "pyops.PyProjectOps",
    s3dir_deployed: "S3Path",
    source_sha256: T.Optional[str] = None,
    tags: T.Optional[T.Dict[str, str]] = None,
    check=True,
    step: str = StepEnum.deploy_chalice_app.value,
    truth_table: T.Optional[tt4human.TruthTable] = truth_table,
    url: T.Optional[str] = None,
) -> T.Tuple["S3Path", bool]:
    s3path_deployed_json = s3dir_deployed / f"{env_name}.json"

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
            return s3path_deployed_json, False

    logger.info(
        f"upload the deployed {env_name}.json file to "
        f"{s3path_deployed_json.console_url}"
    )
    s3path_deployed_json, flag = upload_deployed_json(
        env_name=env_name,
        bsm_devops=bsm_devops,
        pyproject_ops=pyproject_ops,
        s3dir_deployed=s3dir_deployed,
        source_sha256=source_sha256,
        tags=tags,
    )
    if flag is False:
        logger.error("no existing deployed json file found, skip upload", indent=1)
    return s3path_deployed_json, flag
