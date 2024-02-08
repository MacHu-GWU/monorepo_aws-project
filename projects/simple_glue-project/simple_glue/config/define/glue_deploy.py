# -*- coding: utf-8 -*-

"""
AWS Glue deployment related configurations.
"""

import typing as T
import dataclasses

from s3pathlib import S3Path
from aws_glue_artifact.api import GluePythonLibArtifact

from ...paths import dir_python_lib, dir_build_glue

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import Env


@dataclasses.dataclass
class GlueDeployMixin:
    """
    AWS Glue deployment related configurations.
    """
    aws_region: T.Optional[str] = dataclasses.field(default=None)

    @property
    def s3dir_glue_artifacts(self: "Env") -> S3Path:
        """
        Where you store AWS Glue artifacts in S3.

        example: ``${s3dir_artifacts}/glue/versioned-artifacts/``
        """
        return self.s3dir_artifacts.joinpath("glue", "versioned-artifacts").to_dir()

    @property
    def glue_extra_py_files_artifact_name(self: "Env") -> str:
        """
        The glue extra py files artifact name. Usually the:
        "${project_name_snake}-glue-extra_py_files"
        """
        return f"{self.project_name_snake}-extra_py_files"

    def get_glue_extra_py_files_artifact(self: "Env") -> GluePythonLibArtifact:
        """
        The Glue Python library artifact repository.

        See also: https://github.com/MacHu-GWU/aws_glue_artifact-project
        """
        return GluePythonLibArtifact(
            aws_region=self.aws_region,
            s3_bucket=self.s3dir_glue_artifacts.bucket,
            s3_prefix=self.s3dir_glue_artifacts.key,
            artifact_name=self.glue_extra_py_files_artifact_name,
            dir_glue_python_lib=dir_python_lib,
            dir_glue_build=dir_build_glue,
        )
