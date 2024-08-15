# -*- coding: utf-8 -*-

"""
This module provides utilities for managing DynamoDB table exports to S3.

It includes functions for base64 encoding/decoding, datetime conversions,
and a main class for tracking and managing DynamoDB export jobs.

requirements::

    aws_dynamodb_io>=0.1.3,<1.0.0
    fast_dynamodb_json>=0.1.1,<1.0.0
    jsonpickle>=3.0.0,<4.0.0
"""

import typing as T
import gzip
import dataclasses
from datetime import datetime

import jsonpickle
import botocore.exceptions
import polars as pl
from s3pathlib import S3Path
from aws_dynamodb_io.api import ExportJob
from fast_dynamodb_json.api import T_SIMPLE_SCHEMA, deserialize_df
from s3manifesto.api import KeyEnum
from dbsnaplake.api import DBSnapshotFileGroupManifestFile, T_OPTIONAL_KWARGS

from .utils import dt_to_str

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client


@dataclasses.dataclass
class DynamoDBTableArn:
    account_id: str = dataclasses.field()
    region: str = dataclasses.field()
    name: str = dataclasses.field()

    @classmethod
    def from_arn(cls, str: str):
        parts = str.split(":")
        return cls(account_id=parts[4], region=parts[3], name=parts[5].split("/")[-1])

    def to_arn(self) -> str:
        return f"arn:aws:dynamodb:{self.region}:{self.account_id}:table/{self.name}"


@dataclasses.dataclass
class DynamoDBExportManager:
    """
    Manage DynamoDB table exports to S3 and avoid duplicate exports.

    This class uses an S3 folder to track DynamoDB export data. Each unique combination of
    DynamoDB table ARN and export point in time becomes a unique S3 object,
    storing the DynamoDB export metadata. This allows checking if a point-in-time
    DynamoDB export already exists and retrieval of historical export information,
    even after the DynamoDB table export expires on the AWS side.

    :param s3dir_uri:: The S3 URI of the directory used for tracking exports.
    """

    s3dir_uri: str = dataclasses.field()

    @property
    def s3dir(self) -> S3Path:
        return S3Path(self.s3dir_uri).to_dir()

    def get_s3path(
        self,
        table_arn: str,
        export_time: datetime,
    ):
        """
        Generate the S3 path for storing export metadata.
        """
        arn_obj = DynamoDBTableArn.from_arn(table_arn)
        return self.s3dir.joinpath(
            arn_obj.account_id,
            arn_obj.region,
            arn_obj.name,
            dt_to_str(export_time) + ".json",
        )

    def write(
        self,
        s3_client: "S3Client",
        export_job: "ExportJob",
    ):
        """
        Write export job metadata to S3.
        """
        s3path = self.get_s3path(
            table_arn=export_job.table_arn,
            export_time=export_job.export_time,
        )
        # dynamodb export may have datetime, we need to use jsonpickle
        content = jsonpickle.dumps(dataclasses.asdict(export_job))
        s3path.write_text(content, bsm=s3_client, content_type="application/json")

    def read(
        self,
        s3_client: "S3Client",
        table_arn: str,
        export_time: datetime,
    ) -> T.Optional["ExportJob"]:
        """
        Read export job metadata from S3.
        """
        s3path = self.get_s3path(
            table_arn=table_arn,
            export_time=export_time,
        )
        try:
            content = s3path.read_text(bsm=s3_client)
            data = jsonpickle.loads(content)
            return ExportJob(**data)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            else:  # pragma: no cover
                raise e


def dynamodb_json_file_to_polars_dataframe(
    s3_client: "S3Client",
    uri: str,
    simple_schema: T_SIMPLE_SCHEMA,
    scan_ndjson_kwargs: T_OPTIONAL_KWARGS = None,
    n_lines: T.Optional[int] = None,
) -> pl.DataFrame:
    """
    Read one DynamoDB export JSON file from S3 and convert it to a Polars DataFrame.

    :param s3_client: ``boto3.client("s3")``.
    :param uri: The S3 URI of the DynamoDB export ``json.gz`` file.
    :param simple_schema: DynamoDB item data schema.

        >>> from fast_dynamodb_json.api import String, Integer, Float, Bool, List, Struct
        >>> simple_schema = {
        ...     "OrderID": String(),
        ...     "CustomerID": String(),
        ...     "OrderDate": String(),
        ...     "TotalAmount": Float(),
        ...     "ShipmentDetails": Struct({
        ...         "StreetAddress": String(),
        ...         "City": String(),
        ...         "State": String(),
        ...         "ZipCode": String(),
        ...     }),
        ...     "Items": List(...),
        ... }

    :return: A Polars DataFrame.
    """
    b = gzip.decompress(S3Path.from_s3_uri(uri).read_bytes(bsm=s3_client))
    dynamodb_json_schema = {
        k: v.to_dynamodb_json_polars() for k, v in simple_schema.items()
    }
    if scan_ndjson_kwargs is None:
        scan_ndjson_kwargs = {}
    if n_lines is not None:
        scan_ndjson_kwargs["n_rows"] = n_lines
    df = pl.read_ndjson(
        b,
        schema={"Item": pl.Struct(dynamodb_json_schema)},
        **scan_ndjson_kwargs,
    )
    df = deserialize_df(
        df=df,
        simple_schema=simple_schema,
        dynamodb_json_col="Item",
    )
    return df


def many_dynamodb_json_file_to_polars_dataframe(
    s3_client: "S3Client",
    uri_list: T.List[str],
    simple_schema: T_SIMPLE_SCHEMA,
    scan_ndjson_kwargs: T_OPTIONAL_KWARGS = None,
    n_lines: T.Optional[int] = None,
) -> pl.DataFrame:
    """
    Read many DynamoDB export JSON file from S3 and convert it to a Polars DataFrame.

    :param s3_client: ``boto3.client("s3")``.
    :param uri_list: The list of S3 URI of the DynamoDB export ``json.gz`` file.
    :param simple_schema: DynamoDB item data schema.

    :return: A Polars DataFrame.
    """
    sub_df_list = list()
    for uri in uri_list:
        sub_df = dynamodb_json_file_to_polars_dataframe(
            s3_client=s3_client,
            uri=uri,
            simple_schema=simple_schema,
            scan_ndjson_kwargs=scan_ndjson_kwargs,
            n_lines=n_lines,
        )
        sub_df_list.append(sub_df)
    df = pl.concat(sub_df_list)
    return df


def db_snapshot_file_group_manifest_file_to_polars_dataframe(
    db_snapshot_file_group_manifest_file: DBSnapshotFileGroupManifestFile,
    s3_client: "S3Client",
    simple_schema: T_SIMPLE_SCHEMA,
    scan_ndjson_kwargs: T_OPTIONAL_KWARGS = None,
    n_lines: T.Optional[int] = None,
) -> pl.DataFrame:
    return many_dynamodb_json_file_to_polars_dataframe(
        s3_client=s3_client,
        uri_list=[
            data_file[KeyEnum.URI]
            for data_file in db_snapshot_file_group_manifest_file.data_file_list
        ],
        simple_schema=simple_schema,
        scan_ndjson_kwargs=scan_ndjson_kwargs,
        n_lines=n_lines,
    )
