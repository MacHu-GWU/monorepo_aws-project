# -*- coding: utf-8 -*-

"""
Glue Job configurations.
"""

import typing as T
import dataclasses

from pathlib_mate import Path
from s3pathlib import S3Path
from boltons.strutils import slugify, under2camel
from versioned.api import LATEST_VERSION
from aws_glue_artifact.api import GlueETLScriptArtifact

from ...paths import dir_glue_jobs

if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager
    from .main import Env


@dataclasses.dataclass
class GlueJob:
    """
    Represent the configuration of a glue job. They are mostly the required
    arguments for `cdk.glue.CfnJob <https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_glue/CfnJob.html>`_.

    :param env: back reference to the Env object
    :param glue_version: example "4.0", "3.0", "2.0"
        see: https://docs.aws.amazon.com/glue/latest/dg/release-notes.html
    :param worker_type: example "Standard", "G.1X", "G.2X"
        see: https://docs.aws.amazon.com/glue/latest/dg/add-job.html
    :param number_of_workers: see CDK doc
    :param max_concurrent_runs: see CDK doc
    :param max_retries: see CDK doc
    :param timeout: see CDK doc
    :param lib_live_version: the Glue Python lib artifact version for deployment,
        if null, then use the LATEST.
    :param script_live_version: the Glue ETL script artifact version for deployment,
        if null, then use the LATEST.
    :param short_name: short name of the glue job.
    """

    env: "Env" = dataclasses.field(init=False)
    short_name: T.Optional[str] = dataclasses.field(default=None)
    glue_version: T.Optional[str] = dataclasses.field(default=None)
    worker_type: T.Optional[str] = dataclasses.field(default=None)
    number_of_workers: T.Optional[int] = dataclasses.field(default=None)
    max_concurrent_runs: T.Optional[int] = dataclasses.field(default=None)
    max_retries: T.Optional[int] = dataclasses.field(default=None)
    timeout: T.Optional[int] = dataclasses.field(default=None)
    lib_live_version: T.Optional[int] = dataclasses.field(default=None)
    script_live_version: T.Optional[int] = dataclasses.field(default=None)

    @property
    def name(self) -> str:
        """
        Full name of the glue job.
        """
        return f"{self.env.project_name_snake}-{self.env.env_name}-{self.short_name}"

    @property
    def artifact_name(self) -> str:
        """
        Artifact name of the glue job, it is environment agnostic.
        """
        return f"{self.env.project_name_snake}-{self.short_name}"

    @property
    def short_name_slug(self) -> str:
        return slugify(self.short_name, delim="-")

    @property
    def short_name_snake(self) -> str:
        return slugify(self.short_name, delim="_")

    @property
    def short_name_camel(self) -> str:
        """
        The lambda function short name in camel case. This is usually used
        in CloudFormation logic ID.
        """
        return under2camel(slugify(self.short_name, delim="_"))

    @property
    def target_lib_live_version(self) -> str:
        """
        Get the target Glue Python library version you want to set as ALIAS 'LIVE'.
        If the live version is not specified, use the '$LATEST' version.
        """
        return (
            LATEST_VERSION
            if self.lib_live_version is None
            else str(self.lib_live_version)
        )

    @property
    def target_script_live_version(self) -> str:
        """
        Get the target Glue ETL script version you want to set as ALIAS 'LIVE'.
        If the live version is not specified, use the '$LATEST' version.
        :return:
        """
        return (
            LATEST_VERSION
            if self.script_live_version is None
            else str(self.script_live_version)
        )

    def get_s3path_glue_extra_py_files_zip(
        self,
        bsm_devops: "BotoSesManager",
    ) -> S3Path:  # pragma: no cover
        """
        example: ``${s3dir_artifacts}/glue/versioned-artifacts/${prefix_name_snake}_extra_py_files/${version}.zip``
        """
        return self.env.get_glue_extra_py_files_artifact().get_artifact_s3path(
            bsm=bsm_devops,
            version=self.target_lib_live_version,
        )

    @property
    def immutable_artifact_name(self) -> str:
        """
        The artifact name for immutable artifact. Usually the:
        "${project_name}-${short_name}-immutable"
        """
        return f"{self.artifact_name}-immutable"

    @property
    def mutable_artifact_name(self) -> str:
        """
        The artifact name for mutable artifact. Usually the:
        "${project_name}-${env_name}-${short_name}-mutable"
        """
        return f"{self.artifact_name}-mutable"

    @property
    def path_glue_script(self) -> Path:
        return dir_glue_jobs.joinpath(self.short_name + ".py")

    def get_glue_script_content(self) -> bytes:
        return self.path_glue_script.read_bytes()

    def get_immutable_glue_etl_script_artifact(self) -> GlueETLScriptArtifact:
        """
        Get the immutable Glue ETL script artifact object.

        See also: https://github.com/MacHu-GWU/aws_glue_artifact-project
        """
        return GlueETLScriptArtifact(
            aws_region=self.env.aws_region,
            s3_bucket=self.env.s3dir_glue_artifacts.bucket,
            s3_prefix=self.env.s3dir_glue_artifacts.key,
            artifact_name=self.immutable_artifact_name,
            path_glue_etl_script=self.path_glue_script,
        )

    def get_mutable_glue_etl_script_artifact(self) -> GlueETLScriptArtifact:
        """
        Get the mutable Glue ETL script artifact object.

        See also: https://github.com/MacHu-GWU/aws_glue_artifact-project
        """
        return GlueETLScriptArtifact(
            aws_region=self.env.aws_region,
            s3_bucket=self.env.s3dir_glue_artifacts.bucket,
            s3_prefix=self.env.s3dir_glue_artifacts.key,
            artifact_name=self.mutable_artifact_name,
            path_glue_etl_script=self.path_glue_script,
        )

    def get_s3path_immutable_etl_script_py(
        self,
        bsm_devops: "BotoSesManager",
    ) -> S3Path:  # pragma: no cover
        """
        example: ``${s3dir_artifacts}/glue/versioned-artifacts/${project_name}-${env_name}-${short_name}-immutable/${version}.zip``
        """
        return self.get_immutable_glue_etl_script_artifact().get_artifact_s3path(
            bsm=bsm_devops,
            version=self.target_script_live_version,
        )

    def get_s3path_mutable_etl_script_py(
        self,
        bsm_devops: "BotoSesManager",
    ) -> S3Path:  # pragma: no cover
        """
        example: ``${s3dir_artifacts}/glue/versioned-artifacts/${project_name}-${env_name}-${short_name}-mutable/${version}.zip``
        """
        return self.get_mutable_glue_etl_script_artifact().get_artifact_s3path(
            bsm=bsm_devops,
            version=self.target_script_live_version,
        )


@dataclasses.dataclass
class GlueJobMixin:
    glue_jobs: T.Dict[str, GlueJob] = dataclasses.field(default_factory=dict)

    @property
    def glue_job_name_list(self) -> T.List[str]:
        """
        Example::

            >>> GlueJobMixin().glue_job_name_list
            [
                '${project_name}-${env_name}-${short_name1}',
                '${project_name}-${env_name}-${short_name2}',
                '${project_name}-${env_name}-${short_name3}',
            ]
        """
        return [glue_job.name for glue_job in self.glue_jobs.values()]

    @property
    def glue_job_list(self) -> T.List[GlueJob]:
        """
        :class:`GlueJob` object list.
        """
        return list(self.glue_jobs.values())

    # enumerate glue ETL jobs here
    @property
    def glue_unnest(self) -> GlueJob:
        return self.glue_jobs["unnest"]
