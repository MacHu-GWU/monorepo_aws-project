# -*- coding: utf-8 -*-

"""
Lambda function deployment related configurations.
"""

import typing as T
import dataclasses

from s3pathlib import S3Path

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import Env


@dataclasses.dataclass
class LambdaDeployMixin:
    """
    Lambda function deployment related configurations.
    """
    @property
    def chalice_app_name(self: "Env") -> str:
        """
        If you use AWS Chalice framework to deploy your lambda function,
        it is the chalice app name.

        See more details at: https://aws.github.io/chalice/?badge=latest
        """
        return self.project_name_snake

    @property
    def lambda_layer_name(self: "Env") -> str:
        """
        Lambda function layer name.

        Because the Lambda layer is an immutable artifact, we only need one
        lambda layer across all envs, so we don't need to include env name in the
        layer name.
        """
        return self.project_name_snake

    @property
    def s3dir_lambda(self: "Env") -> S3Path:
        """
        Where you store lambda related artifacts.

        example: ``${s3dir_artifacts}/lambda/``
        """
        return self.s3dir_artifacts.joinpath("lambda").to_dir()
