# -*- coding: utf-8 -*-

# helpers
from automation.pyproject import pyproject_ops
from automation.logger import logger
from automation.emoji import Emoji
from automation.git import (
    GIT_BRANCH_NAME,
    GIT_COMMIT_ID,
    GIT_COMMIT_MESSAGE,
    create_git_tag,
    IS_CLEAN_UP_BRANCH,
    IS_CLEAN_UP_COMMIT,
)

# actions
from automation.tests import run_int_test
from automation.deploy import deploy_app, delete_app

# app code
from simple_lambda.paths import dir_cdk
from simple_lambda.boto_ses import bsm
from simple_lambda.config.init import EnvEnum, config


@logger.start_and_end(
    msg="Clean Up",
    start_emoji=f"{Emoji.delete}",
    end_emoji=Emoji.delete,
    pipe=Emoji.delete,
)
def clean_up():
    """
    Run clean up only when we are on the 'cleanup' branch and the commit message
    is in the format of 'cleanup: <env_name1>, <env_name2>, ...'. The list of
    env name in the commit message will be used to delete the corresponding app.

    This is a dangerous operation, so we have to ensure developers know what
    they are doing.
    """
    if IS_CLEAN_UP_BRANCH and IS_CLEAN_UP_COMMIT:
        for _env in EnvEnum:
            env_name = _env.value
            if env_name in GIT_COMMIT_MESSAGE:
                env = config.get_env(env_name)
                with logger.nested():
                    delete_app(
                        bsm=bsm,
                        dir_cdk=dir_cdk,
                        stack_name=env.cloudformation_stack_name,
                        prod_env_name=EnvEnum.prd.value,
                        env_name=env.env_name,
                        check=True,
                    )
            else:
                logger.info(
                    f"{Emoji.red_circle} Skip deleting app for environment {env_name!r} "
                    f"because it is not in GIT_COMMIT_MESSAGE: {GIT_COMMIT_MESSAGE!r}."
                )
    else:
        logger.info(
            f"{Emoji.red_circle} we only do clean up from 'cleanup' branch "
            f"with commit message pattern 'cleanup: <env_name1>, <env_name2>, ...'"
            f"your are on {GIT_BRANCH_NAME!r} branch and the commit message is {GIT_COMMIT_MESSAGE!r}."
        )


@logger.start_and_end(
    msg="Build Phase",
    start_emoji=f"{Emoji.start} {Emoji.build_phase}",
    end_emoji=Emoji.build_phase,
    pipe=Emoji.build_phase,
)
def build_phase():
    with logger.nested():
        deploy_app(
            bsm=bsm,
            config=config,
            s3dir_lambda=config.env.s3dir_lambda,
            tags=config.env.aws_tags,
            dir_cdk=dir_cdk,
            stack_name=config.env.cloudformation_stack_name,
            prod_env_name=EnvEnum.prd.value,
            env_name=config.env.env_name,
            check=True,
        )
        run_int_test(
            prod_env_name=EnvEnum.prd.value,
            env_name=config.env.env_name,
            check=True,
        )
        create_git_tag(
            tag_name=f"{pyproject_ops.package_name}-{pyproject_ops.package_version}",
            commit_id=GIT_COMMIT_ID,
            env_name=config.env.env_name,
            prod_env_name=EnvEnum.prd.value,
            check=True,
        )
        clean_up()


build_phase()
