# -*- coding: utf-8 -*-

"""
lambda app deployment automation script.
"""

import typing as T
from pathlib_mate import Path

from .aws_console import get_aws_console
from .runtime import IS_CI
from .git import (
    GIT_BRANCH_NAME,
    IS_MASTER_BRANCH,
    IS_LAMBDA_BRANCH,
    IS_RELEASE_BRANCH,
    IS_CLEAN_UP_BRANCH,
)

from .logger import logger
from .emoji import Emoji
from .env import CURRENT_ENV
from .build import build_lambda_source
from .iac import cdk_deploy, cdk_destroy
from .deploy_rule import do_we_deploy_app, do_we_delete_app

if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path
    from simple_lambda.config.define import Env, Config


@logger.start_and_end(
    msg="Publish new Lambda version",
    start_emoji=Emoji.awslambda,
    error_emoji=f"{Emoji.failed} {Emoji.awslambda}",
    end_emoji=f"{Emoji.succeeded} {Emoji.awslambda}",
    pipe=Emoji.awslambda,
)
def publish_lambda_version(
    bsm: "BotoSesManager",
    config: "Config",
    prod_env_name: str,
    env_name: str = CURRENT_ENV,
):
    """
    Publish a new lambda version from latest.
    """
    if env_name != prod_env_name:
        logger.info(
            f"{Emoji.red_circle} don't publish new version for {env_name!r} env,"
            f"only do that in production env."
        )
        return
    env: "Env" = config.get_env(env_name=env_name)
    aws_console = get_aws_console(bsm=bsm)
    url = aws_console.awslambda.filter_functions(f"{env.project_name}-{env.env_name}")
    logger.info(f"preview deployed lambda functions: {url}")
    for lambda_function in env.lambda_functions.values():
        url = aws_console.awslambda.get_function(lambda_function.name)
        logger.info(f"preview lambda function {lambda_function.name!r}: {url}", 1)
        lambda_function.publish_version(bsm=bsm)


@logger.start_and_end(
    msg="Deploy App",
    start_emoji=f"{Emoji.deploy}",
    error_emoji=f"{Emoji.failed} {Emoji.deploy}",
    end_emoji=f"{Emoji.succeeded} {Emoji.deploy}",
    pipe=Emoji.deploy,
)
def deploy_app(
    bsm: "BotoSesManager",
    config: "Config",
    s3dir_lambda: "S3Path",
    tags: T.Dict[str, str],
    dir_cdk: Path,
    stack_name: str,
    prod_env_name: str,
    env_name: str = CURRENT_ENV,
    check: bool = True,
):
    logger.info(f"deploy app to {env_name!r} env ...")
    if check:
        if (
            do_we_deploy_app(
                env_name=env_name,
                prod_env_name=prod_env_name,
                is_ci_runtime=IS_CI,
                branch_name=GIT_BRANCH_NAME,
                is_master_branch=IS_MASTER_BRANCH,
                is_lambda_branch=IS_LAMBDA_BRANCH,
                is_release_branch=IS_RELEASE_BRANCH,
            )
            is False
        ):
            return

    with logger.nested():
        build_lambda_source(
            bsm=bsm,
            s3dir_lambda=s3dir_lambda,
            tags=tags,
            verbose=False,
        )
        cdk_deploy(
            env_name=env_name,
            bsm=bsm,
            dir_cdk=dir_cdk,
            stack_name=stack_name,
        )
        publish_lambda_version(
            bsm=bsm,
            config=config,
            prod_env_name=prod_env_name,
            env_name=env_name,
        )


@logger.start_and_end(
    msg="Delete App",
    start_emoji=f"{Emoji.delete}",
    error_emoji=f"{Emoji.failed} {Emoji.delete}",
    end_emoji=f"{Emoji.succeeded} {Emoji.delete}",
    pipe=Emoji.delete,
)
def delete_app(
    bsm: "BotoSesManager",
    dir_cdk: Path,
    stack_name: str,
    prod_env_name: str,
    env_name: str = CURRENT_ENV,
    check: bool = True,
):
    logger.info(f"delete app from {env_name!r} env ...")
    if check:
        if (
            do_we_delete_app(
                env_name=env_name,
                prod_env_name=prod_env_name,
                is_ci_runtime=IS_CI,
                branch_name=GIT_BRANCH_NAME,
                is_cleanup_branch=IS_CLEAN_UP_BRANCH,
            )
            is False
        ):
            return

    with logger.nested():
        cdk_destroy(
            env_name=env_name,
            bsm=bsm,
            dir_cdk=dir_cdk,
            stack_name=stack_name,
        )
