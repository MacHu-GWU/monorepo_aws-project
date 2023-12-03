# -*- coding: utf-8 -*-

"""
This module implements the Git branch strategy related automation.

- main branch:
    - name pattern: exactly equal to ``main`` or ``master``
- feature branch:
    - name pattern: starts with ``feat`` or ``feature``
- fix branch:
    - name pattern: starts with ``fix``
- layer branch:
    - usage: deploy AWS Lambda Layer
    - name pattern: starts with ``layer``
- ecr branch:
    - usage: build ECR image
    - name pattern: starts with ``ecr``
- lambda branch:
    - usage: deploy AWS Lambda Function
    - name pattern: starts with ``lbd`` or ``lambda``
- doc branch:
    - usage: build and deploy documentation to S3
    - name pattern: starts with ``doc`` or ``docs``
- release branch:
    - name pattern: starts with ``rls`` or ``release``
- cleanup branch:
    - usage: deploy AWS Lambda Function
    - name pattern: starts with ``clean`` or ``cleanup``
"""

import os
import subprocess
from textwrap import dedent

from aws_codecommit import (
    better_boto,
    is_certain_semantic_commit,
    is_certain_semantic_branch,
)

from .vendor.git_cli import (
    get_git_branch_from_git_cli,
    get_git_commit_id_from_git_cli,
    get_commit_message_by_commit_id,
)
from .pyproject import pyproject_ops
from .runtime import IS_LOCAL, IS_CI
from .logger import logger
from .emoji import Emoji
from .git_rule import do_we_create_git_tag


dir_repo = pyproject_ops.dir_project_root.parent.parent

if IS_LOCAL:
    GIT_BRANCH_NAME: str = get_git_branch_from_git_cli(dir_repo)
    GIT_COMMIT_ID: str = get_git_commit_id_from_git_cli(dir_repo)
    GIT_COMMIT_MESSAGE: str = get_commit_message_by_commit_id(dir_repo, GIT_COMMIT_ID)
elif IS_CI:
    GIT_BRANCH_NAME: str = os.environ["GITHUB_REF_NAME"]
    GIT_COMMIT_ID: str = os.environ["GITHUB_SHA"]

    from boto_session_manager import BotoSesManager

    bsm = BotoSesManager()
    GIT_REPO_NAME = os.environ["GITHUB_REPOSITORY"].split("/", 1)[1]
    # GIT_COMMIT_MESSAGE = better_boto.get_commit(
    #     bsm=bsm,
    #     repo_name=GIT_REPO_NAME,
    #     commit_id=GIT_COMMIT_ID,
    # ).message
    GIT_COMMIT_MESSAGE = "unknown"
else:
    raise NotImplementedError

# branch name could be:
# main
# ${project_name}/${semantic_name}/${description}
parts = GIT_BRANCH_NAME.split("/", 1)
if len(parts) == 1:  # if main branch
    SEMANTIC_BRANCH_NAME = parts[0]
else:
    SEMANTIC_BRANCH_NAME = parts[-1]


def print_git_info():
    logger.info(f"Current git branch is ⤵️ {GIT_BRANCH_NAME!r}")
    logger.info(f"Current git commit is ✅ {GIT_COMMIT_ID!r}")
    logger.info(f"Current git commit message is ✅ {GIT_COMMIT_MESSAGE!r}")


IS_MASTER_BRANCH: bool = SEMANTIC_BRANCH_NAME in ["main", "master"]
IS_FEATURE_BRANCH: bool = is_certain_semantic_branch(
    SEMANTIC_BRANCH_NAME, ["feat", "feature"]
)
IS_FIX_BRANCH: bool = is_certain_semantic_branch(SEMANTIC_BRANCH_NAME, ["fix"])
IS_LAYER_BRANCH: bool = is_certain_semantic_branch(SEMANTIC_BRANCH_NAME, ["layer"])
IS_ECR_BRANCH: bool = is_certain_semantic_branch(SEMANTIC_BRANCH_NAME, ["ecr"])
IS_LAMBDA_BRANCH: bool = is_certain_semantic_branch(
    SEMANTIC_BRANCH_NAME, ["lbd", "lambda"]
)
IS_DOC_BRANCH: bool = is_certain_semantic_branch(SEMANTIC_BRANCH_NAME, ["doc", "docs"])
IS_RELEASE_BRANCH: bool = is_certain_semantic_branch(
    SEMANTIC_BRANCH_NAME, ["rls", "release"]
)
IS_CLEAN_UP_BRANCH: bool = is_certain_semantic_branch(
    SEMANTIC_BRANCH_NAME, ["clean", "cleanup"]
)

IS_CLEAN_UP_COMMIT: bool = is_certain_semantic_commit(
    GIT_COMMIT_MESSAGE, ["clean", "cleanup"]
)

def _create_git_tag(tag_name: str, commit_id: str):
    """
    Reference:

    - https://docs.aws.amazon.com/codecommit/latest/userguide/how-to-create-tag.html
    """
    args = [
        "git",
        "tag",
        tag_name,
        commit_id,
    ]
    res = subprocess.run(args, check=True)

    args = [
        "git",
        "push",
        "origin",
        tag_name,
    ]
    subprocess.run(args, check=True)


@logger.start_and_end(
    msg="Create Git Tag Unit Test",
    start_emoji=Emoji.label,
    error_emoji=f"{Emoji.failed} {Emoji.label}",
    end_emoji=f"{Emoji.succeeded} {Emoji.label}",
    pipe=Emoji.label,
)
def create_git_tag(
    tag_name: str,
    commit_id: str,
    env_name: str,
    prod_env_name: str,
    check: bool = True,
):
    """
    Create a new git tag using ${project_name}-${project_version}.
    """
    if check:
        if (
            do_we_create_git_tag(
                is_ci_runtime=IS_CI,
                env_name=env_name,
                prod_env_name=prod_env_name,
                branch_name=GIT_BRANCH_NAME,
                is_release_branch=IS_RELEASE_BRANCH,
            )
            is False
        ):
            return

    if IS_CI:
        # install git-remote-codecommit
        subprocess.run(["pip", "install", "git-remote-codecommit"], check=True)
        subprocess.run(["pyenv", "rehash"], check=True)
        repo_name = os.environ["USER_GIT_REPO_NAME"]
        repo_url = f"codecommit::us-east-1://{repo_name}"
        # clone the repo in the project root
        with pyproject_ops.dir_project_root.temp_cwd():
            subprocess.run(
                ["git", "clone", repo_url, "--quiet"],
                capture_output=True,
                check=True,
            )
        # CD in there then create the tag and then push it
        with pyproject_ops.dir_project_root.joinpath(repo_name).temp_cwd():
            _create_git_tag(tag_name=tag_name, commit_id=commit_id)
    else:
        _create_git_tag(tag_name=tag_name, commit_id=commit_id)


@logger.start_and_end(
    msg="bump version",
    start_emoji=Emoji.label,
    error_emoji=f"{Emoji.failed} {Emoji.label}",
    end_emoji=f"{Emoji.succeeded} {Emoji.label}",
    pipe=Emoji.label,
)
def bump_version(
    major: bool = False,
    minor: bool = False,
    patch: bool = False,
):
    if sum([patch, minor, major]) != 1:
        raise ValueError(
            "Only one and exact one of 'is_patch', 'is_minor', 'is_major' can be True"
        )

    # get the current version
    major, minor, micro = pyproject_ops.package_version.split(".")
    major, minor, micro = int(major), int(minor), int(micro)

    # update version
    if major:
        action = "major"
        major += 1
        minor, micro = 0, 0
        # print(f"{major}.{minor}.{mirco}")
    elif minor:
        action = "minor"
        minor += 1
        micro = 0
    elif patch:
        action = "patch"
        micro += 1
    else:  # pragma: no cover
        raise NotImplementedError
    new_version = f"{major}.{minor}.{micro}"

    # update _version.py file
    version_py_content = dedent(
        """
    __version__ = "{}"

    # keep this ``if __name__ == "__main__"``, don't delete!
    # this is used by automation script to detect the project version
    if __name__ == "__main__":  # pragma: no cover
        print(__version__)
    """
    ).strip()
    version_py_content = version_py_content.format(new_version)
    pyproject_ops.path_version_py.write_text(version_py_content)

    # update pyproject.toml file
    with pyproject_ops.dir_project_root.temp_cwd():
        args = [
            pyproject_ops.path_bin_poetry,
            "version",
            action,
        ]
        subprocess.run(args, check=True)
