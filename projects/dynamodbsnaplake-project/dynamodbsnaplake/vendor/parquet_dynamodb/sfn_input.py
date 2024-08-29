# -*- coding: utf-8 -*-

"""
The :class:`SfnInput` class is a thin glue layer between the
AWS Step Functions input and the ``dbsnaplake.api.Project`` class,
where the data processing logic is implemented.
"""

# standard library
import typing as T
import os
import sys
import textwrap
import importlib
import dataclasses
from datetime import datetime
from pathlib import Path
from functools import cached_property

# third party
import boto3
from s3pathlib import S3Path
import polars as pl
from aws_dynamodb_io.api import ExportJob, ExportFormatEnum
from dbsnaplake.api import (
    S3Location,
    DBSnapshotFileGroupManifestFile,
    Project,
)
from polars_writer.api import Writer
from jsonpolars.api import parse_dfop
from .vendor.fast_dynamodb_json.api import (
    T_SIMPLE_SCHEMA,
    json_type_to_simple_type,
)

try:
    import duckdb

    has_duckdb = True
except ImportError:  # pragma: no cover
    has_duckdb = False

from .utils import dt_to_str
from .dynamodb import (
    DynamoDBTableArn,
    DynamoDBExportManager,
    db_snapshot_file_group_manifest_file_to_polars_dataframe,
)
from .sentinel import NOTHING, REQUIRED, OPTIONAL

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client
    from mypy_boto3_dynamodb.client import DynamoDBClient


# in AWS Lambda, the /tmp directory is the only writable directory
if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:  # pragma: no cover
    dir_tmp = Path("/tmp")
# in local development, we use the current directory
else:  # pragma: no cover
    dir_tmp = Path.home() / "tmp"
path_workflow_settings = dir_tmp / "workflow_settings.py"


@dataclasses.dataclass
class SfnInput:
    """
    Represents the input data of an AWS Step Functions execution.

    .. note::

        这个 dataclass 的所有属性都是可以被 JSON 序列化的, 而不能是复杂的 Python 对象.
        例如 ``s3uri_staging_dir`` 定义了我们的 staging 数据存储的 S3 URI, 这个是一个字符串,
        但是在后续的操作中我们会将这个字符串转换成 :class:`s3pathlib.S3Path` 对象.
        为了保证这个 dataclass 跟 StepFunction Input 兼容, 所以这个属性我们就以字符串的形式
        存储.

    --- Core parameter
    :param table_arn: ARN of the DynamoDB table to export.
    :param export_time: The DynamoDB export time in ISO format.
    :param s3uri_staging: S3 URI where staging data is stored.
    :param s3uri_database: S3 URI where the final data lake files will be stored.

    # --- Transformation logic related
    :param transforms: dataframe transformation logic written in JSON format.
    :param col_record_id: which column is considered as the unique record id.
        for DynamoDB table only has partition key, use a string, for DynamoDB table
        has both partition key and sort key, use a tuple of two string.
        If not provided, then you cannot write it to datalake format like
        Deltalake, Hudi, Iceburg.
    :param col_create_time: which column is considered as the immutable create time
        of a record.
    :param col_partition_keys: which columns is considered as the partition keys.
        if not given, then we end up with ONE file in the final datalake.
    :param col_record_count: which column is used to count the number of records.
        this column cannot have NULL value in all records. If not given, then we
        don't check number of records in the validation result.
    :param create_datalake: if False, skip the data lake ingestion step. We end up
        with a parquet datalake in the staging folder.
    :param sort_by: List of column names to sort by before writing to parquet.
    :param descending: List of booleans indicating if the sort is descending.
    :param target_db_snapshot_file_group_size: Target size for DB snapshot file groups.
    :param target_parquet_file_size: Target size for parquet files.
    :param count_on_column: Column name to count on when validating the final datalake.
        if not given, then we don't check number of records in the validation result.
    :param s3uri_datalake_override: verride the generated data lake S3 URI.
    """

    # fmt: off
    # --- Core parameter
    table_arn: str = dataclasses.field(default=REQUIRED)
    export_time: str = dataclasses.field(default=REQUIRED)
    s3uri_staging_dir: str = dataclasses.field(default=REQUIRED)
    s3uri_database_dir: str = dataclasses.field(default=REQUIRED)
    s3uri_datalake_override: T.Optional[str] = dataclasses.field(default=None)

    # --- Transformation logic related
    schema: T.Dict[str, T.Dict[str, T.Any]] = dataclasses.field(default_factory=dict)
    transforms: T.List[T.Dict[str, T.Any]] = dataclasses.field(default_factory=list)
    col_record_id: T.Optional[T.Union[str, T.Tuple[str, str]]] = dataclasses.field(default=None)
    col_create_time: T.Optional[str] = dataclasses.field(default=None)
    col_partition_keys: T.Optional[T.List[str]] = dataclasses.field(default=None)
    col_record_count: T.Optional[str] = dataclasses.field(default=None)
    create_datalake: bool = dataclasses.field(default=True)
    sort_by: T.List[str] = dataclasses.field(default_factory=list)
    descending: T.List[bool] = dataclasses.field(default_factory=list)

    # --- Output configuration
    target_db_snapshot_file_group_size: int = dataclasses.field(default=128_000_000)
    target_parquet_file_size: int = dataclasses.field(default=128_000_000)
    writer_options: T.Optional[T.Dict[str, T.Any]] = dataclasses.field(default=None)
    gzip_compression: bool = dataclasses.field(default=False)
    # fmt: on

    def __post_init__(self):
        if self.s3uri_staging_dir.endswith("/") is False:
            self.s3uri_staging_dir = self.s3uri_staging_dir + "/"
        if self.s3uri_database_dir.endswith("/") is False:
            self.s3uri_database_dir = self.s3uri_database_dir + "/"

    @cached_property
    def table_name(self) -> str:
        """
        Extract and return the table name from the table ARN.
        """
        return self.table_arn.split("/")[-1]

    @cached_property
    def table_name_lower_snake_case(self) -> str:
        """
        Return the table name in lower snake case format.
        """
        return self.table_name.lower().replace("-", "_")

    @cached_property
    def table_arn_obj(self) -> DynamoDBTableArn:
        """
        Return a :class:`parquet_dynamodb.dynamodb.DynamoDBTableArn` object
        created from the table ARN.
        """
        return DynamoDBTableArn.from_arn(self.table_arn)

    @cached_property
    def export_datetime(self) -> datetime:
        """
        Convert the export_time string to a datetime object.
        """
        return datetime.fromisoformat(self.export_time)

    @cached_property
    def export_time_str(self) -> str:
        """
        Return a formatted string representation of the export time.
        """
        return dt_to_str(self.export_datetime)

    @cached_property
    def _s3dir_staging(self) -> S3Path:
        return S3Path.from_s3_uri(self.s3uri_staging_dir)

    @cached_property
    def _s3dir_database(self) -> S3Path:
        return S3Path.from_s3_uri(self.s3uri_database_dir)

    @cached_property
    def _s3dir_dynamodb_export_manager(self) -> S3Path:
        return self._s3dir_staging.joinpath("exports_history").to_dir()

    @cached_property
    def export_manager(self) -> DynamoDBExportManager:
        """
        Return a :class`parquet_dynamodb.dynamodb.DynamoDBExportManager` object
        for managing exports.
        """
        return DynamoDBExportManager(s3dir_uri=self._s3dir_dynamodb_export_manager.uri)

    @cached_property
    def s3dir_dynamodb_export(self) -> S3Path:
        return self._s3dir_staging.joinpath("exports").to_dir()

    def run_or_get_dynamodb_export(
        self,
        s3_client: "S3Client",
        dynamodb_client: "DynamoDBClient",
    ) -> T.Tuple["ExportJob", bool]:
        """
        Run a new DynamoDB export job or retrieve an existing one.

        This method checks if an export job for the specified table and time already exists.
        If not, it initiates a new export job. It then monitors the job status and raises
        an error if the job fails.
        """
        export_job = self.export_manager.read(
            s3_client=s3_client,
            table_arn=self.table_arn,
            export_time=self.export_datetime,
        )
        if export_job is None:
            is_already_launched = False
            export_job = ExportJob.export_table_to_point_in_time(
                dynamodb_client=dynamodb_client,
                table_arn=self.table_arn,
                export_time=self.export_datetime,
                s3_bucket=self.s3dir_dynamodb_export.bucket,
                s3_prefix=self.s3dir_dynamodb_export.key,
                export_format=ExportFormatEnum.DYNAMODB_JSON.value,
            )
            self.export_manager.write(s3_client=s3_client, export_job=export_job)
        else:
            is_already_launched = True

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

        return export_job, is_already_launched

    @cached_property
    def s3_loc(self) -> S3Location:
        """
        Derive the :class:`dbsnaplake.s3_loc.S3Location` object to access
        important S3 locations.
        """
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
        """
        todo: docstring
        """
        return self.s3_loc.s3dir_staging_manifest.joinpath("manifest-data.parquet")

    @cached_property
    def s3path_db_snapshot_manifest_summary(self) -> S3Path:
        """
        todo: docstring
        """
        return self.s3_loc.s3dir_staging_manifest.joinpath("manifest-summary.json")

    @cached_property
    def s3path_snapshot_to_staging_worker_payload(self):
        """
        todo: docstring
        """
        return self.s3_loc.s3dir_staging_manifest.joinpath(
            "snapshot_to_staging_worker_payload.json"
        )

    @cached_property
    def s3path_staging_to_datalake_worker_payload(self):
        """
        todo: docstring
        """
        return self.s3_loc.s3dir_staging_manifest.joinpath(
            "staging_to_datalake_worker_payload.json"
        )

    @cached_property
    def s3dir_datalake(self) -> S3Path:
        """
        todo: docstring
        """
        return self.s3_loc.s3dir_datalake

    @cached_property
    def s3dir_sfn_ctx(self) -> S3Path:
        """
        todo: docstring
        """
        return self._s3dir_staging.joinpath("sfn_ctx").to_dir()

    @cached_property
    def simple_schema(self) -> T_SIMPLE_SCHEMA:
        simple_schema = {}
        for k, v in self.schema.items():
            simple_schema[k] = json_type_to_simple_type(v)
        return simple_schema

    def batch_read_snapshot_data_file(
        self,
        db_snapshot_file_group_manifest_file: DBSnapshotFileGroupManifestFile,
        s3_client: "S3Client",
        **kwargs,
    ) -> pl.DataFrame:
        """ """
        df = db_snapshot_file_group_manifest_file_to_polars_dataframe(
            db_snapshot_file_group_manifest_file=db_snapshot_file_group_manifest_file,
            s3_client=s3_client,
            simple_schema=self.simple_schema,
            **kwargs,
        )
        for transform in self.transforms:
            op = parse_dfop(transform)
            df = op.to_polars(df)
        return df

    @property
    def default_writer(self) -> Writer:
        return Writer(
            format="parquet",
            parquet_compression="snappy",
        )

    @cached_property
    def writer(self) -> Writer:
        if self.writer_options is None:
            writer = self.default_writer
        else:
            writer = Writer(**self.writer_options)
        return writer

    def to_dict(self) -> T.Dict[str, T.Any]:
        """
        Serialize the object to a dictionary that is ready to be used in
        ``boto3.client("stepfunctions").start_execution(..., input=...)``.
        """
        return dict(
            table_arn=self.table_arn,
            export_time=self.export_time,
            s3uri_staging_dir=self.s3uri_staging_dir,
            s3uri_database_dir=self.s3uri_database_dir,
            s3uri_datalake_override=self.s3uri_datalake_override,
            schema=self.schema,
            transforms=self.transforms,
            col_record_id=self.col_record_id,
            col_create_time=self.col_create_time,
            col_partition_keys=self.col_partition_keys,
            col_record_count=self.col_record_count,
            create_datalake=self.create_datalake,
            sort_by=self.sort_by,
            descending=self.descending,
            target_db_snapshot_file_group_size=self.target_db_snapshot_file_group_size,
            target_parquet_file_size=self.target_parquet_file_size,
            writer_options=self.writer_options,
            gzip_compression=self.gzip_compression,
        )

    @classmethod
    def from_dict(cls, dct: T.Dict[str, T.Any]):
        """
        Restore the :class:`SfnInput` object from input data.
        """
        return cls(**dct)

    @cached_property
    def project(self) -> Project:
        """
        Derive the :class:`dbsnaplake.project.Project` object to access data
        processing methods.
        """
        return Project(
            s3_client=None,  # s3_client will be set later in the lambda function handler
            s3uri_db_snapshot_manifest_summary=self.s3path_db_snapshot_manifest_summary.uri,
            s3uri_staging=self.s3_loc.s3dir_staging.uri,
            s3uri_datalake=self.s3_loc.s3dir_datalake.uri,
            target_db_snapshot_file_group_size=self.target_db_snapshot_file_group_size,
            partition_keys=self.col_partition_keys,
            create_datalake=self.create_datalake,
            sort_by=self.sort_by,
            descending=self.descending,
            target_parquet_file_size=self.target_parquet_file_size,
            polars_writer=self.writer,
            gzip_compression=self.gzip_compression,
            count_column=self.col_record_count,
            tracker_table_name="parquet_dynamodb_tracker",
            aws_region="us-east-1",
            use_case_id=f"{self.table_arn_obj.account_id}_{self.table_arn_obj.region}_{self.table_arn_obj.name}_{self.export_time_str}",
        )

    def _setup_duckdb(
        self,
        boto_ses: "boto3.Session",
        more_duckdb_config: T.Optional[T.List[str]] = None,
    ):
        """
        Set up the DuckDB environment for reading data from S3.
        """
        # common SQL snippet
        # enable the httpfs (HTTP file system plugin https://duckdb.org/docs/extensions/httpfs), so we can read data from AWS S3
        sql_httpfs = textwrap.dedent(
            f"""
        INSTALL httpfs;
        LOAD httpfs;
        """
        )

        # set AWS credential
        credentials = boto_ses.get_credentials()

        lines = [
            "SET s3_region='us-east-1';",
            f"SET s3_access_key_id='{credentials.access_key}';",
            f"SET s3_secret_access_key='{credentials.secret_key}';",
        ]
        if credentials.token:
            lines.append(f"SET s3_session_token='{credentials.token}';")
        if more_duckdb_config:
            lines.extend(more_duckdb_config)
        sql_credential = "\n".join(lines)

        duckdb.sql(sql_httpfs)
        duckdb.sql(sql_credential)

    @property
    def duckdb_from_table(self) -> str:
        """
        Derive the "table name" part of the "SELECT FROM ..." SQL query.
        Basically, it tells duckdb to read the parquet data from the S3 datalake location.
        """
        uri = self.s3_loc.s3dir_datalake.uri
        partition_keys = self.col_partition_keys
        if partition_keys:
            hive_partition_part = f", hive_partitioning={len(partition_keys)}"
        else:
            hive_partition_part = ""
        sql_from_table_all_parquet = (
            f"read_parquet('{uri}**/*.parquet'{hive_partition_part})"
        )
        return sql_from_table_all_parquet

    def run_sql(
        self,
        boto_ses: "boto3.Session",
        sql: str,
        more_duckdb_config: T.Optional[T.List[str]] = None,
    ):
        '''
        Run a SQL query using DuckDB.

        Usage example::

            import textwrap

            sql = textwrap.dedent(
                f"""
            SELECT
                *
            FROM {sfn_input.duckdb_from_table} t
            LIMIT 10
            ;
            """
            )

            res = sfn_input.run_sql(sql)
            res.show()
        '''
        self._setup_duckdb(
            boto_ses=boto_ses,
            more_duckdb_config=more_duckdb_config,
        )
        return duckdb.sql(sql)
