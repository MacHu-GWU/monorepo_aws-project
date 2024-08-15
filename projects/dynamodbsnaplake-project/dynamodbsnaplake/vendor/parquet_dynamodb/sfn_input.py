# -*- coding: utf-8 -*-

"""
AWS Step Functions Context Management Module

This module provides utilities and classes for managing AWS Step Functions execution context,
including serialization, deserialization, and S3 storage operations.
"""

import typing as T
import sys
import importlib
import dataclasses
from datetime import datetime
from pathlib import Path
from functools import cached_property

from s3pathlib import S3Path
from aws_dynamodb_io.api import ExportJob, ExportFormatEnum
from fast_dynamodb_json.api import T_SIMPLE_SCHEMA
from dbsnaplake.api import (
    S3Location,
    DerivedColumn,
    Project,
    T_BatchReadSnapshotDataFileCallable,
)

from .utils import dt_to_str
from .dynamodb import DynamoDBTableArn, DynamoDBExportManager

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client
    from mypy_boto3_dynamodb.client import DynamoDBClient


dir_here = Path(__file__).absolute().parent
dir_tmp = dir_here / "tmp"
path_workflow_settings = dir_tmp / "workflow_settings.py"


def s3uri_staging_dir_to_s3uri_sfn_ctx_dir(
    s3uri_staging_dir: str,
) -> str:
    if s3uri_staging_dir.endswith("/") is False:
        s3uri_staging_dir = s3uri_staging_dir + "/"
    s3uri_sfn_ctx_dir = f"{s3uri_staging_dir}sfn_ctx/"
    return s3uri_sfn_ctx_dir


@dataclasses.dataclass
class SfnInput:
    """
    Represents the input data of an AWS Step Functions execution.

    :param table_arn: arn of the dynamodb table you want to export.
    :param export_time: the dynamodb export time, in ISO format.
    :param s3uri_staging: where you store all staging data
    :param s3uri_database: where you want to store
    :param s3uri_python_module:
    :param sort_by:
    :param descending:
    :param s3uri_datalake_override:
    """

    # fmt: off
    table_arn: str = dataclasses.field()
    export_time: str = dataclasses.field()
    s3uri_staging_dir: str = dataclasses.field()
    s3uri_database_dir: str = dataclasses.field()
    s3uri_python_module: T.Optional[str] = dataclasses.field()
    sort_by: T.List[str] = dataclasses.field()
    descending: T.List[bool] = dataclasses.field()
    s3uri_datalake_override: T.Optional[str] = dataclasses.field()
    # in production, these attribute are imported from the s3uri_python_module
    extract_record_id_override: T.Optional[DerivedColumn] = dataclasses.field(default=None)
    extract_create_time_override: T.Optional[DerivedColumn] = dataclasses.field(default=None)
    extract_update_time_override: T.Optional[DerivedColumn] = dataclasses.field(default=None)
    extract_partition_keys_override: T.Optional[T.List[DerivedColumn]] = dataclasses.field(default=None)
    simple_schema_override: T.Optional[T_SIMPLE_SCHEMA]  = dataclasses.field(default=None)
    batch_read_snapshot_data_file_override: T.Optional[T_BatchReadSnapshotDataFileCallable] = dataclasses.field(default=None)
    # fmt: on

    def __post_init__(self):
        if self.s3uri_staging_dir.endswith("/") is False:
            self.s3uri_staging_dir = self.s3uri_staging_dir + "/"
        if self.s3uri_database_dir.endswith("/") is False:
            self.s3uri_database_dir = self.s3uri_database_dir + "/"
        if self.s3uri_python_module is not None:
            if self.s3uri_python_module.endswith("/"):
                raise ValueError("s3uri_python_module should not end with '/'")

    # --------------------------------------------------------------------------
    # import from python module
    #
    # User can pass in a JSON object as StepFunction input. However, some
    # user defined customization cannot be declared by JSON, so we allow user
    # to implement a python module to define these customization. And the
    # execution engine can download this python module from S3 and import it.
    # --------------------------------------------------------------------------
    def download_python_module(self, s3_client: "S3Client"):
        """
        Download the python module from S3 and save it to a temporary directory.
        This temporary directory is a fixed location next to this module.
        """
        if self.s3uri_python_module is None:
            return
        dir_tmp.mkdir(exist_ok=True)
        s3path = S3Path.from_s3_uri(self.s3uri_python_module)
        content = s3path.read_text(bsm=s3_client)
        path_workflow_settings.write_text(content)

    @cached_property
    def _imported_python_module(self):
        """
        Import the Python module from the temporary directory.
        """
        if path_workflow_settings.exists() is False:
            raise FileNotFoundError(
                f"{path_workflow_settings} not found, "
                f"you may need to run Project.download_python_module(s3_client=...) first."
            )
        sys.path.append(str(dir_tmp))
        module = importlib.import_module(path_workflow_settings.stem)
        return module

    @property
    def _py_mod_extract_record_id(self):
        return getattr(self._imported_python_module, "extract_record_id")

    @property
    def _py_mod_extract_create_time(self):
        return getattr(self._imported_python_module, "extract_create_time")

    @property
    def _py_mod_extract_update_time(self):
        return getattr(self._imported_python_module, "extract_update_time")

    @property
    def _py_mod_extract_partition_keys(self):
        return getattr(self._imported_python_module, "extract_partition_keys")

    @property
    def _py_mod_simple_schema(self):
        return getattr(self._imported_python_module, "SIMPLE_SCHEMA")

    @property
    def _py_mod_batch_read_snapshot_data_file(self):
        return getattr(self._imported_python_module, "batch_read_snapshot_data_file")

    @cached_property
    def table_name(self) -> str:
        return self.table_arn.split("/")[-1]

    @cached_property
    def table_name_lower_snake_case(self) -> str:
        return self.table_name.lower().replace("-", "_")

    @cached_property
    def table_arn_obj(self) -> DynamoDBTableArn:
        return DynamoDBTableArn.from_arn(self.table_arn)

    @cached_property
    def export_datetime(self) -> datetime:
        return datetime.fromisoformat(self.export_time)

    @cached_property
    def export_time_str(self) -> str:
        return dt_to_str(self.export_datetime)

    @cached_property
    def _s3dir_staging(self) -> S3Path:
        return S3Path.from_s3_uri(self.s3uri_staging_dir)

    @cached_property
    def _s3dir_database(self) -> S3Path:
        return S3Path.from_s3_uri(self.s3uri_database_dir)

    @cached_property
    def s3path_python_module(self) -> T.Optional[S3Path]:
        if self.s3uri_python_module is None:
            return None
        return S3Path.from_s3_uri(self.s3uri_python_module)

    @cached_property
    def _s3dir_dynamodb_export_manager(self) -> S3Path:
        return self._s3dir_staging.joinpath("exports_history").to_dir()

    @cached_property
    def export_manager(self) -> DynamoDBExportManager:
        return DynamoDBExportManager(s3dir_uri=self._s3dir_dynamodb_export_manager.uri)

    @cached_property
    def _s3dir_dynamodb_export(self) -> S3Path:
        return self._s3dir_staging.joinpath("exports").to_dir()

    def run_or_get_dynamodb_export(
        self,
        s3_client: "S3Client",
        dynamodb_client: "DynamoDBClient",
    ) -> "ExportJob":
        """
        If we never run the export job before, we will run it.

        """
        export_job = self.export_manager.read(
            s3_client=s3_client,
            table_arn=self.table_arn,
            export_time=self.export_datetime,
        )
        if export_job is None:
            export_job = ExportJob.export_table_to_point_in_time(
                dynamodb_client=dynamodb_client,
                table_arn=self.table_arn,
                export_time=self.export_datetime,
                s3_bucket=self._s3dir_dynamodb_export.bucket,
                s3_prefix=self._s3dir_dynamodb_export.key,
                export_format=ExportFormatEnum.DYNAMODB_JSON.value,
            )
            self.export_manager.write(s3_client=s3_client, export_job=export_job)

        export_job.get_details(dynamodb_client=dynamodb_client)

        if export_job.is_failed():
            s3path = self.export_manager.get_s3path(
                table_arn=self.table_arn,
                export_time=self.export_datetime,
            )
            s3path.delete(s3_client=s3_client)
            raise SystemError(
                f"Export job {export_job.arn} failed! "
                f"Please check what went wrong before doing another try! "
                f"You may need to manually delete the {s3path.uri} tracker file before doing another export. "
                f"S3 console url: {s3path.console_url}"
            )

        return export_job

    @cached_property
    def s3_loc(self) -> S3Location:
        if self.s3uri_datalake_override:
            s3uri_datalake = self.s3uri_datalake_override
        else:
            s3uri_datalake = (
                self._s3dir_database.joinpath(
                    f"{self.table_name_lower_snake_case}_{self.export_time_str}"
                )
                .to_dir()
                .uri
            )

        return S3Location(
            s3uri_staging=self._s3dir_staging.joinpath(
                self.table_arn_obj.account_id,
                self.table_arn_obj.region,
                self.table_arn_obj.name,
                self.export_time_str,
            )
            .to_dir()
            .uri,
            s3uri_datalake=s3uri_datalake,
        )

    @cached_property
    def s3path_db_snapshot_manifest_data(self) -> S3Path:
        return self.s3_loc.s3dir_staging_manifest.joinpath("manifest-data.parquet")

    @cached_property
    def s3path_db_snapshot_manifest_summary(self) -> S3Path:
        return self.s3_loc.s3dir_staging_manifest.joinpath("manifest-summary.json")

    @cached_property
    def s3path_snapshot_to_staging_worker_payload(self):
        return self.s3_loc.s3dir_staging_manifest.joinpath("snapshot_to_staging_worker_payload.json")

    @cached_property
    def s3path_staging_to_datalake_worker_payload(self):
        return self.s3_loc.s3dir_staging_manifest.joinpath("staging_to_datalake_worker_payload.json")

    @cached_property
    def s3dir_datalake(self) -> S3Path:
        """ """
        return self.s3_loc.s3dir_datalake

    @cached_property
    def s3dir_sfn_ctx(self) -> S3Path:
        return self._s3dir_staging.joinpath("sfn_ctx").to_dir()

    def to_dict(self) -> T.Dict[str, T.Any]:
        return dict(
            table_arn=self.table_arn,
            export_time=self.export_time,
            s3uri_staging_dir=self.s3uri_staging_dir,
            s3uri_database_dir=self.s3uri_database_dir,
            s3uri_python_module=self.s3uri_python_module,
            sort_by=self.sort_by,
            descending=self.descending,
            s3uri_datalake_override=self.s3uri_datalake_override,
        )

    @classmethod
    def from_dict(cls, dct: T.Dict[str, T.Any]):
        return cls(**dct)

    @cached_property
    def project(self) -> Project:
        if self.extract_record_id_override is not None:
            extract_record_id = self.extract_record_id_override
        else:
            extract_record_id = self._py_mod_extract_record_id

        if self.extract_create_time_override is not None:
            extract_create_time = self.extract_create_time_override
        else:
            extract_create_time = self._py_mod_extract_create_time

        if self.extract_update_time_override is not None:
            extract_update_time = self.extract_update_time_override
        else:
            extract_update_time = self._py_mod_extract_update_time

        if self.extract_partition_keys_override is not None:
            extract_partition_keys = self.extract_partition_keys_override
        else:
            extract_partition_keys = self._py_mod_extract_partition_keys

        return Project(
            s3_client=None,
            s3uri_db_snapshot_manifest_summary=self.s3path_db_snapshot_manifest_summary.uri,
            s3uri_staging=self.s3_loc.s3dir_staging.uri,
            s3uri_datalake=self.s3_loc.s3dir_datalake.uri,
            # todo: this should be dynamic
            target_db_snapshot_file_group_size=256_000_000,
            extract_record_id=extract_record_id,
            extract_create_time=extract_create_time,
            extract_update_time=extract_update_time,
            extract_partition_keys=extract_partition_keys,
            sort_by=self.sort_by,
            descending=self.descending,
            # todo: this should be dynamic
            target_parquet_file_size=128_000_000,
            tracker_table_name="parquet_dynamodb_tracker",
            aws_region="us-east-1",
            use_case_id=f"{self.table_arn_obj.account_id}_{self.table_arn_obj.region}_{self.table_arn_obj.name}_{self.export_time_str}",
        )
