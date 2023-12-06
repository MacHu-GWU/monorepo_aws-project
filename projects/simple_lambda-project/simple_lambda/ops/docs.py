# -*- coding: utf-8 -*-

import typing as T

import aws_ops_alpha.api as aws_ops_alpha

from ..logger import logger
from ..runtime import runtime
from ..git import git_repo
from .pyproject import pyproject_ops

Emoji = aws_ops_alpha.Emoji


def _do_we_deploy_doc() -> bool:
    """
    Code saver.
    """
    return aws_ops_alpha.simple_lambda.do_we_deploy_doc(
        is_ci_runtime=runtime.is_ci,
        branch_name=git_repo.git_branch_name,
        is_doc_branch=git_repo.is_doc_branch,
    )


@logger.emoji_block(
    msg="Build Documentation Site Locally",
    emoji=Emoji.doc,
)
def build_doc(
    check: bool = True,
):
    if check:
        if _do_we_deploy_doc() is False:
            return

    pyproject_ops.build_doc()


def view_doc():
    pyproject_ops.view_doc()


def _get_aws_cli_profile_arg() -> T.Optional[str]:
    if runtime.is_local:
        from simple_lambda.boto_ses import boto_ses_factory

        return boto_ses_factory.bsm_devops.profile_name
    elif runtime.is_ci:
        return None
    else:  # pragma: no cover
        raise NotImplementedError


@logger.emoji_block(
    msg="Deploy Documentation Site To S3 as Versioned Doc",
    emoji=Emoji.doc,
)
def deploy_versioned_doc(
    check: bool = True,
):
    if check:
        if _do_we_deploy_doc() is False:
            return
    from simple_lambda.config.init import config

    pyproject_ops.deploy_versioned_doc(
        bucket=config.env.s3bucket_docs,
        aws_profile=_get_aws_cli_profile_arg(),
    )


@logger.emoji_block(
    msg="Deploy Documentation Site To S3 as Latest Doc",
    emoji=Emoji.doc,
)
def deploy_latest_doc(
    check: bool = True,
):
    if check:
        if _do_we_deploy_doc() is False:
            return

    from simple_lambda.config.init import config

    pyproject_ops.deploy_latest_doc(
        bucket=config.env.s3bucket_docs,
        aws_profile=_get_aws_cli_profile_arg(),
    )


def view_latest_doc():
    from simple_lambda.config.init import config

    pyproject_ops.view_latest_doc(bucket=config.env.s3bucket_docs)
