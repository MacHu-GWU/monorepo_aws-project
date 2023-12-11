# -*- coding: utf-8 -*-

"""
This module implements the Git branch strategy related automation.
"""

import typing as T
import os
import dataclasses
from pathlib import Path
from functools import cached_property

from .vendor import semantic_branch as sem_branch
from .vendor.git_cli import (
    get_git_branch_from_git_cli,
    get_git_commit_id_from_git_cli,
    get_commit_message_by_commit_id,
)

from .constants import AwsOpsSemanticBranchEnum
from .runtime import runtime
from .logger import logger


InvalidSemanticNameError = sem_branch.InvalidSemanticNameError
SemanticBranchRule = sem_branch.SemanticBranchRule


@dataclasses.dataclass
class GitRepo:
    dir_repo: Path = dataclasses.field()
    sem_branch_rule: T.Optional[SemanticBranchRule] = dataclasses.field(default=None)

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

    def print_git_info(
        self,
        verbose: bool = True,
    ):
        if verbose:  # pragma: no cover
            logger.info(f"Current git branch is 🔀 {self.git_branch_name!r}")
            logger.info(f"Current git commit is # {self.git_commit_id!r}")
            logger.info(f"Current git commit message is 📜 {self.git_commit_message!r}")

    @cached_property
    def semantic_branch_part(self) -> str:
        raise NotImplementedError

    @cached_property
    def semantic_branch_name(self) -> str:
        return self.sem_branch_rule.parse_semantic_name(self.semantic_branch_part)

    # --------------------------------------------------------------------------
    # Identify common semantic branch type
    # --------------------------------------------------------------------------
    @property
    def is_main_branch(self) -> bool:
        return sem_branch.is_main_branch(self.semantic_branch_part)

    @property
    def is_feature_branch(self) -> bool:
        return sem_branch.is_feature_branch(self.semantic_branch_part)

    @property
    def is_fix_branch(self) -> bool:
        return sem_branch.is_fix_branch(self.semantic_branch_part)

    @property
    def is_doc_branch(self) -> bool:
        return sem_branch.is_doc_branch(self.semantic_branch_part)

    @property
    def is_release_branch(self) -> bool:
        return sem_branch.is_release_branch(self.semantic_branch_part)

    @property
    def is_cleanup_branch(self) -> bool:
        return sem_branch.is_cleanup_branch(self.semantic_branch_part)

    # --------------------------------------------------------------------------
    # Identify AWS Ops semantic branch type
    # --------------------------------------------------------------------------
    @property
    def is_lambda_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.semantic_branch_part,
            [AwsOpsSemanticBranchEnum.lbd, AwsOpsSemanticBranchEnum.awslambda],
        )

    @property
    def is_layer_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.semantic_branch_part,
            [AwsOpsSemanticBranchEnum.layer],
        )

    @property
    def is_ecr_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.semantic_branch_part,
            [AwsOpsSemanticBranchEnum.ecr],
        )

    @property
    def is_ami_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.semantic_branch_part,
            [AwsOpsSemanticBranchEnum.ami],
        )

    @property
    def is_glue_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.semantic_branch_part,
            [AwsOpsSemanticBranchEnum.glue],
        )

    @property
    def is_sfn_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.semantic_branch_part,
            [AwsOpsSemanticBranchEnum.sfn],
        )

    @property
    def is_airflow_branch(self) -> bool:
        return sem_branch.is_certain_semantic_branch(
            self.semantic_branch_part,
            [AwsOpsSemanticBranchEnum.airflow],
        )


def extract_semantic_branch_name_for_multi_repo(git_branch_name: str) -> str:
    """
    Extract the semantic branch name from the full git branch name.

    Examples::

        >>> extract_semantic_branch_name_for_multi_repo("main")
        'main'
        >>> extract_semantic_branch_name_for_multi_repo("feature/add-this-feature")
        'feature'
    """
    return git_branch_name.split("/")[0]


def extract_semantic_branch_name_for_mono_repo(git_branch_name: str) -> str:
    """
    Extract the semantic branch name from the full git branch name.
    Since this is mono repo, the first part of the full git branch usually
    are the project name, we are looking for the second part.

    Examples::

        >>> extract_semantic_branch_name_for_multi_repo("main")
        'main'
        >>> extract_semantic_branch_name_for_multi_repo("my_project/feature/add-this-feature")
        'feature'
    """
    parts = git_branch_name.split("/")
    if parts[0].lower().strip() in ("main", "master"):
        return parts[0]
    else:
        return parts[1]


@dataclasses.dataclass
class MultiGitRepo(GitRepo):  # pragma: no cover
    """
    Each project is held on an entirely separate, version-controlled repository.
    """

    @cached_property
    def semantic_branch_part(self) -> str:
        return extract_semantic_branch_name_for_multi_repo(self.git_branch_name)


@dataclasses.dataclass
class MonoGitRepo(GitRepo):  # pragma: no cover
    """
    A monorepo is a version-controlled code repository that holds many projects.
    While these projects may be related, they are often logically independent
    and run by different teams
    """

    @cached_property
    def semantic_branch_part(self) -> str:
        return extract_semantic_branch_name_for_mono_repo(self.git_branch_name)
