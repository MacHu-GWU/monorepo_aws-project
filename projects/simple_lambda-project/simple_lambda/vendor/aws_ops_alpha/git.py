# -*- coding: utf-8 -*-

"""
This module implements the Git branch strategy related automation.
"""

import typing as T
import os
import enum
import dataclasses
from pathlib import Path
from functools import cached_property

from .vendor import semantic_branch as sem_branch
from .vendor.git_cli import (
    get_git_branch_from_git_cli,
    get_git_commit_id_from_git_cli,
    get_commit_message_by_commit_id,
)

from .runtime import runtime
from .logger import logger


class AwsOpsSemanticBranchEnum(str, enum.Enum):
    lbd = "new"
    awslambda = "lambda"
    layer = "layer"
    ecr = "ecr"
    ami = "ami"
    glue = "glue"
    sfn = "sfn"
    airflow = "airflow"


@dataclasses.dataclass
class GitRepo:
    dir_repo: Path = dataclasses.field()

    # --------------------------------------------------------------------------
    # Get git information from runtime environment
    # --------------------------------------------------------------------------
    @cached_property
    def git_branch_name(self) -> T.Optional[str]:  # pragma: no cover
        """
        Return the human friendly git branch name. Some CI vendor would use
        ``refs/heads/branch_name``, we only keep the ``branch_name`` part.
        """
        if runtime.is_local:
            return get_git_branch_from_git_cli(self.dir_repo)
        elif runtime.is_aws_codebuild:
            raise NotImplementedError
        elif runtime.is_github_action:
            return os.environ.get("GITHUB_REF_NAME")
        elif runtime.is_gitlab_ci:
            return os.environ.get("CI_COMMIT_BRANCH")
        elif runtime.is_bitbucket_pipeline:
            return os.environ.get("BITBUCKET_BRANCH")
        elif runtime.is_circleci:
            return os.environ["CIRCLE_BRANCH"]
        elif runtime.is_jenkins:
            raise NotImplementedError
        else:
            raise NotImplementedError

    @cached_property
    def git_commit_id(self) -> T.Optional[str]:  # pragma: no cover
        """
        Return the git commit sha1 hash value.
        """
        if runtime.is_local:
            return get_git_commit_id_from_git_cli(self.dir_repo)
        elif runtime.is_aws_codebuild:
            raise NotImplementedError
        elif runtime.is_github_action:
            return os.environ.get("GITHUB_SHA")
        elif runtime.is_gitlab_ci:
            return os.environ.get("CI_COMMIT_SHA")
        elif runtime.is_bitbucket_pipeline:
            return os.environ.get("BITBUCKET_COMMIT")
        elif runtime.is_circleci:
            return os.environ["CIRCLE_SHA1"]
        elif runtime.is_jenkins:
            raise NotImplementedError
        else:
            raise NotImplementedError

    @cached_property
    def git_commit_message(self) -> T.Optional[str]:  # pragma: no cover
        """
        Return the git commit message.
        """
        if runtime.is_local:
            return get_commit_message_by_commit_id(self.dir_repo, self.git_commit_id)
        # note that there's no native way to get commit message from most of
        # CI/CD service vendor, you have to get it yourself and inject that
        # into "USER_GIT_COMMIT_MESSAGE" environment variable.
        elif runtime.is_ci:
            return os.environ.get("USER_GIT_COMMIT_MESSAGE")
        else:
            raise NotImplementedError

    @cached_property
    def semantic_branch_name(self) -> str:
        """
        Extract the semantic branch name from the full git branch name.

        Examples:

        - ``main`` -> ``main``
        - ``${project_name}/${semantic_name}/${description}`` -> ``${semantic_name}/${description}``
        """
        parts = self.git_branch_name.split("/", 1)
        if len(parts) == 1:  # if main branch
            return parts[0]
        else:
            return parts[-1]

    def print_git_info(self):
        logger.info(f"Current git branch is 🔀 {self.git_branch_name!r}")
        logger.info(f"Current git commit is # {self.git_commit_id!r}")
        logger.info(f"Current git commit message is 📜 {self.git_commit_message!r}")

    # --------------------------------------------------------------------------
    # Identify common semantic branch type
    # --------------------------------------------------------------------------
    @property
    def is_main_branch(self) -> bool:
        return sem_branch.is_main_branch(self.git_branch_name)

    @property
    def is_feature_branch(self) -> bool:
        return sem_branch.is_feature_branch(self.git_branch_name)

    @property
    def is_fix_branch(self) -> bool:
        return sem_branch.is_fix_branch(self.git_branch_name)

    @property
    def is_doc_branch(self) -> bool:
        return sem_branch.is_doc_branch(self.git_branch_name)

    @property
    def is_release_branch(self) -> bool:
        return sem_branch.is_release_branch(self.git_branch_name)

    @property
    def is_cleanup_branch(self) -> bool:
        return sem_branch.is_cleanup_branch(self.git_branch_name)

    # --------------------------------------------------------------------------
    # Identify AWS Ops semantic branch type
    # --------------------------------------------------------------------------
    @property
    def is_lambda_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.git_branch_name,
            [AwsOpsSemanticBranchEnum.lbd, AwsOpsSemanticBranchEnum.awslambda],
        )

    @property
    def is_layer_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.git_branch_name,
            [AwsOpsSemanticBranchEnum.layer],
        )

    @property
    def is_ecr_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.git_branch_name,
            [AwsOpsSemanticBranchEnum.ecr],
        )

    @property
    def is_ami_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.git_branch_name,
            [AwsOpsSemanticBranchEnum.ami],
        )

    @property
    def is_glue_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.git_branch_name,
            [AwsOpsSemanticBranchEnum.glue],
        )

    @property
    def is_sfn_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.git_branch_name,
            [AwsOpsSemanticBranchEnum.sfn],
        )

    @property
    def is_airflow_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.git_branch_name,
            [AwsOpsSemanticBranchEnum.airflow],
        )
