# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime

import boto3

from .common import ExecutionContext
from ..logger import logger

PROJECT_NAME = os.environ.get("PROJECT_NAME")
ENV_NAME = os.environ.get("ENV_NAME")
BUCKET = os.environ.get("BUCKET")
PREFIX = os.environ.get("PREFIX")

TIMEOUT = 30

s3_client = boto3.client("s3")
lbd_client = boto3.client("lambda")


def low_level_api(
    s3_client,
    bucket: str,
    prefix: str,
    execution_id: str,
):
    if prefix.endswith("/"):
        prefix = prefix[:-1]

    exec_context = ExecutionContext.read(
        s3_client=s3_client,
        bucket=bucket,
        prefix=prefix,
        exec_id=execution_id,
    )
    if (int(datetime.utcnow().timestamp()) - exec_context.job_start_timestamp) >= 30:
        raise TimeoutError("job run timed out in 30 seconds!")

    response = s3_client.get_object(
        Bucket=bucket,
        Key=f"{prefix}/{execution_id}/status.txt",
    )
    status = response["Body"].read().decode("utf-8").strip()
    return {"status": status}


@logger.start_and_end(
    msg="{func_name}",
)
def lambda_handler(event, context):  # pragma: no cover
    logger.info("received event:")
    logger.info(json.dumps(event, indent=4))
    execution_id = event["Execution"]["Id"].split(":")[-1]
    return low_level_api(
        s3_client=s3_client,
        bucket=BUCKET,
        prefix=PREFIX,
        execution_id=execution_id,
    )
