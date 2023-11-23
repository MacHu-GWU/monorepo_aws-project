# -*- coding: utf-8 -*-

# helpers
from automation.logger import logger
from automation.emoji import Emoji

# actions
from automation.runtime import print_runtime_info
from automation.env import print_env_info
from automation.git import print_git_info
from automation.build import build_lambda_source, build_lambda_layer
from automation.tests import run_cov_test
from automation.docs import build_doc, deploy_versioned_doc, deploy_latest_doc

# app code
from simple_lambda.boto_ses import bsm
from simple_lambda.config.init import config


@logger.start_and_end(
    msg="Pre Build Phase",
    start_emoji=f"{Emoji.start} {Emoji.pre_build_phase}",
    end_emoji=Emoji.pre_build_phase,
    pipe=Emoji.pre_build_phase,
)
def pre_build_phase():
    print_runtime_info()
    print_env_info()
    print_git_info()

    with logger.nested():
        # has to build source before running cov test
        # because the CDK will use the source artifacts
        build_lambda_source(
            bsm=bsm,
            s3dir_lambda=config.env.s3dir_lambda,
            tags=config.env.aws_tags,
            verbose=False,
        )
        run_cov_test(check=True)
        build_doc(check=True)
        deploy_versioned_doc(check=True)
        deploy_latest_doc(check=True)
        build_lambda_layer(
            bsm=bsm,
            layer_name=config.env.lambda_layer_name,
            s3dir_lambda=config.env.s3dir_lambda,
            tags=config.env.aws_tags,
            check=True,
        )


pre_build_phase()
