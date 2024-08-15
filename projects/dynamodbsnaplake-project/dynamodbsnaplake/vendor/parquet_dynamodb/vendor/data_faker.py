# -*- coding: utf-8 -*-

"""
We will download a sample DynamoDB export data (1M Amazon Order data) from
https://github.com/MacHu-GWU/fast_dynamodb_json-project/releases/tag/0.1.1

And upload the data to S3 bucket for testing.
"""

import typing as T
import json
import dataclasses
from pathlib import Path
from urllib import request

from s3pathlib import S3Path
from s3manifesto.api import KeyEnum
from dbsnaplake.api import DBSnapshotManifestFile, DBSnapshotFileGroupManifestFile

from ..paths import dir_unit_test

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client

dir_tmp = dir_unit_test / "tmp"
dir_tmp.mkdir(exist_ok=True)


def download_file(url: str, path: Path):
    """
    Download file from URL to local path.
    """
    with request.urlopen(url) as response:
        with path.open("wb") as f:
            f.write(response.read())


release_url = (
    "https://github.com/MacHu-GWU/fast_dynamodb_json-project/releases/download/0.1.1/"
)
manifest_file_name = "manifest-files.json"
path_manifest_file = dir_tmp / manifest_file_name


def download_manifest_file():
    """
    Download manifest file to local as a cache.
    """
    if path_manifest_file.exists() is False:
        url = release_url + manifest_file_name
        download_file(url, path_manifest_file)


@dataclasses.dataclass
class DataFile:
    """
    Represent a data file in the manifest file.
    """

    file: str
    item_count: int


def read_manifest_file() -> T.List[DataFile]:
    """
    Read ``{dir_tmp}/manifest-files.json``
    """
    lines = path_manifest_file.read_text().splitlines()
    rows = [json.loads(line) for line in lines]
    data_file_list = [
        DataFile(
            file=row["dataFileS3Key"].split("/")[-1],
            item_count=row["itemCount"],
        )
        for row in rows
    ]
    return data_file_list


def download_data_files():
    """
    Download data files to local.
    """
    data_file_list = read_manifest_file()
    for data_file in data_file_list:
        url = release_url + data_file.file
        path_data_file = dir_tmp / data_file.file
        if path_data_file.exists() is False:
            download_file(url, path_data_file)


def prepare_s3_bucket_for_testing(
    s3_client: "S3Client",
    s3dir_export: "S3Path",
    s3path_manifest_summary: "S3Path",
    s3path_manifest_data: "S3Path",
):
    """
    Run this function to prepare S3 bucket for testing.
    """
    if s3path_manifest_summary.exists(bsm=s3_client):
        return

    # upload data files to s3
    data_file_list = read_manifest_file()
    db_snapshot_manifest_data_file_list = list()
    for data_file in data_file_list:
        path = dir_tmp / data_file.file
        s3path = s3dir_export / data_file.file
        s3path_new = s3path.write_bytes(path.read_bytes(), bsm=s3_client)
        db_snapshot_manifest_data_file = {
            KeyEnum.URI: s3path.uri,
            KeyEnum.ETAG: s3path_new.etag,
            KeyEnum.SIZE: path.stat().st_size,
            KeyEnum.N_RECORD: data_file.item_count,
        }
        db_snapshot_manifest_data_file_list.append(db_snapshot_manifest_data_file)

    db_snapshot_manifest_file = DBSnapshotManifestFile.new(
        uri=s3path_manifest_data.uri,
        uri_summary=s3path_manifest_summary.uri,
        data_file_list=db_snapshot_manifest_data_file_list,
        calculate=True,
    )
    db_snapshot_manifest_file.write(s3_client=s3_client)
