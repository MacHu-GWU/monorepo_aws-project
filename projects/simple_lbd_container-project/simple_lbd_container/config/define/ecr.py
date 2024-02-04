# -*- coding: utf-8 -*-

"""
ECR related configurations.
"""

import typing as T
import dataclasses


if T.TYPE_CHECKING:  # pragma: no cover
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
