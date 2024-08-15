# -*- coding: utf-8 -*-

import typing as T
import polars as pl
from fast_dynamodb_json.api import (
    Integer,
    Float,
    String,
    Bool,
    List,
    Struct,
)
import dbsnaplake.api as dbsnaplake
from dynamodbsnaplake.vendor.parquet_dynamodb.api import (
    db_snapshot_file_group_manifest_file_to_polars_dataframe,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client

extract_record_id = dbsnaplake.DerivedColumn(
    extractor=pl.concat_str(pl.col("CustomerID"), pl.lit("#"), pl.col("OrderID")),
    alias="record_id",
)

extract_create_time = dbsnaplake.DerivedColumn(
    extractor=pl.col("OrderDate").str.to_datetime(),
    alias="create_time",
)

extract_update_time = dbsnaplake.DerivedColumn(
    extractor=pl.col("OrderDate").str.to_datetime(),
    alias="update_time",
)

extract_partition_keys = [
    dbsnaplake.DerivedColumn(
        extractor=pl.col("OrderDate")
        .str.to_datetime()
        .dt.year()
        .cast(pl.Utf8)
        .str.zfill(4),
        alias="year",
    ),
    dbsnaplake.DerivedColumn(
        extractor=pl.col("OrderDate")
        .str.to_datetime()
        .dt.month()
        .cast(pl.Utf8)
        .str.zfill(2),
        alias="month",
    ),
]

SIMPLE_SCHEMA = {
    "OrderID": String(),
    "CustomerID": String(),
    "OrderDate": String(),
    "TotalAmount": Float(),
    "Status": String(),
    "ShippingAddress": Struct(
        {
            "StreetAddress": String(),
            "City": String(),
            "State": String(),
            "ZipCode": String(),
            "Country": String(),
        }
    ),
    "Items": List(
        Struct(
            {
                "ProductID": String(),
                "Name": String(),
                "Price": Float(),
                "Quantity": Integer(),
            }
        ),
    ),
    "AppliedCoupons": List(String()),
    "PaymentMethod": String(),
    "LastFourDigits": String(),
    "EstimatedDeliveryDate": String(),
    "GiftWrap": Bool(),
    "GiftMessage": String(),
}

POLARS_SCHEMA = {k: v.to_polars() for k, v in SIMPLE_SCHEMA.items()}

DYNAMODB_JSON_SCHEMA = {
    k: v.to_dynamodb_json_polars() for k, v in SIMPLE_SCHEMA.items()
}


def batch_read_snapshot_data_file(
    db_snapshot_file_group_manifest_file: dbsnaplake.DBSnapshotFileGroupManifestFile,
    s3_client: "S3Client",
    **kwargs,
) -> pl.DataFrame:
    return db_snapshot_file_group_manifest_file_to_polars_dataframe(
        db_snapshot_file_group_manifest_file=db_snapshot_file_group_manifest_file,
        s3_client=s3_client,
        simple_schema=SIMPLE_SCHEMA,
        **kwargs,
    )
