# -*- coding: utf-8 -*-

import typing as T

from .pyproject import pyproject_ops
from .runtime import IS_LOCAL, IS_CI
from .git import IS_DOC_BRANCH, GIT_BRANCH_NAME
from .logger import logger
from .emoji import Emoji
from .docs_rule import (
    do_we_deploy_doc,
)


def _do_we_deploy_doc() -> bool:
    """
    Code saver.
    """
    return do_we_deploy_doc(
        is_ci_runtime=IS_CI,
        branch_name=GIT_BRANCH_NAME,
        is_doc_branch=IS_DOC_BRANCH,
    )


@logger.start_and_end(
    msg="Build Documentation Site Locally",
    start_emoji=Emoji.doc,
    error_emoji=f"{Emoji.failed} {Emoji.doc}",
    end_emoji=f"{Emoji.succeeded} {Emoji.doc}",
    pipe=Emoji.doc,
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
    if IS_LOCAL:
        from simple_lambda.boto_ses import bsm

        return bsm.profile_name
    elif IS_CI:
        return None
    else:  # pragma: no cover
        raise NotImplementedError


@logger.start_and_end(
    msg="Deploy Documentation Site To S3 as Versioned Doc",
    start_emoji=Emoji.doc,
    error_emoji=f"{Emoji.failed} {Emoji.doc}",
    end_emoji=f"{Emoji.succeeded} {Emoji.doc}",
    pipe=Emoji.doc,
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


@logger.start_and_end(
    msg="Deploy Documentation Site To S3 as Latest Doc",
    start_emoji=Emoji.doc,
    end_emoji=Emoji.doc,
    pipe=Emoji.doc,
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
