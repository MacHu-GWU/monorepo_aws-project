# -*- coding: utf-8 -*-

"""
lambda app deployment automation script.
"""

import typing as T

from pathlib_mate import Path
import aws_console_url.api as aws_console_url
import aws_ops_alpha.api as aws_ops_alpha

from ..config.init import config
from ..boto_ses import boto_ses_factory
from ..logger import logger
from ..runtime import runtime
from ..git import git_repo
from ..env import EnvEnum, get_current_env
from ..paths import dir_cdk

from .pyproject import pyproject_ops
from .build import build_lambda_source

if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path
    from simple_lambda.config.define import Env, Config

Emoji = aws_ops_alpha.Emoji



@logger.emoji_block(
    msg="Publish new Lambda version",
    emoji=Emoji.awslambda,
)
def publish_lambda_version(
    bsm: "BotoSesManager",
    config: "Config",
    prod_env_name: str,
    env_name: T.Optional[str] = None,
):
    """
    Publish a new lambda version from latest.
    """
    if env_name is None:
        env_name = get_current_env()

    if env_name != prod_env_name:
        logger.info(
            f"{Emoji.red_circle} don't publish new version for {env_name!r} env,"
            f"only do that in production env."
        )
        return
    env: "Env" = config.get_env(env_name=env_name)
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm=bsm)
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
    check: bool = True,
):
    env_name = get_current_env()
    logger.info(f"deploy app to {env_name!r} env ...")
    if check:
        if (
            aws_ops_alpha.simple_lambda.do_we_deploy_app(
                env_name=env_name,
                prod_env_name=EnvEnum.prd.value,
                is_local_runtime=runtime.is_local,
                branch_name=git_repo.git_branch_name,
                is_main_branch=git_repo.is_main_branch,
                is_lambda_branch=git_repo.is_lambda_branch,
                is_release_branch=git_repo.is_release_branch,
            )
            is False
        ):
            return

    with logger.nested():
        build_lambda_source()
        bsm = boto_ses_factory.get_app_bsm()
        aws_ops_alpha.cdk_deploy(
            env_name=env_name,
            bsm=boto_ses_factory.get_app_bsm(),
            dir_cdk=dir_cdk,
            stack_name=config.env.cloudformation_stack_name,
            skip_prompt=True,
        )
        publish_lambda_version(
            bsm=bsm,
            config=config,
            prod_env_name=EnvEnum.prd.name,
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
    env_name: T.Optional[str] = None,
    check: bool = True,
):
    if env_name is None:
        env_name = get_current_env()
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


