# -*- coding: utf-8 -*-

"""
ECR related configurations.
"""

import typing as T
import dataclasses


if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager
    from .main import Env


@dataclasses.dataclass
class EcrMixin:
    """
    ECR related configurations.
    """

    @property
    def ecr_repo_name(self: "Env") -> str:
        """
        ECR Repository name.

        Because the ECR container is an immutable artifact, we only need one ECR
        across all envs, so we don't need to include env name in the ECR repo name.
        """
        return self.project_name_snake

    def get_ecr_repo_uri(
        self: "Env",
        bsm_devops: "BotoSesManager",
        tag: str,
    ) -> str:  # pragma: no cover
        """
        Get the full ECR repo URI with image tag.
        """
        return f"{bsm_devops.aws_account_id}.dkr.ecr.{bsm_devops.aws_region}.amazonaws.com/{self.ecr_repo_name}:{tag}"

    def get_ecr_repo_arn(
        self: "Env",
        bsm_devops: "BotoSesManager",
    ) -> str:  # pragma: no cover
        """
        Get the full ECR repo URI with image tag.
        """
        return f"arn:aws:ecr:{bsm_devops.aws_region}:{bsm_devops.aws_account_id}:repository/{self.ecr_repo_name}"
