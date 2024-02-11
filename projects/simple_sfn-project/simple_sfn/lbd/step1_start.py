# -*- coding: utf-8 -*-

import os
import json
import time
from datetime import datetime

import boto3

from .common import ExecutionContext
from ..logger import logger


PROJECT_NAME = os.environ.get("PROJECT_NAME")
ENV_NAME = os.environ.get("ENV_NAME")
BUCKET = os.environ.get("BUCKET")
PREFIX = os.environ.get("PREFIX")

s3_client = boto3.client("s3")
lbd_client = boto3.client("lambda")


def low_level_api(
    s3_client,
    bucket: str,
    prefix: str,
    execution_id: str,
    dry_run: bool = False,
):
    exec_context = ExecutionContext(
        exec_id=execution_id,
        job_start_timestamp=int(datetime.utcnow().timestamp()),
    )
    exec_context.write(s3_client, bucket=bucket, prefix=prefix)
    if dry_run is False:
        lbd_client.invoke(
            FunctionName=f"{PROJECT_NAME}-{ENV_NAME}-s2_run_job",
            InvocationType="Event",
            Payload=json.dumps({"exec_id": exec_context.exec_id}),
        )
    time.sleep(1)
    return {}


@logger.start_and_end(
    msg="{func_name}",
)
def lambda_handler(event, context):  # pragma: no cover
    logger.info("received event:")
    logger.info(json.dumps(event, indent=4))
    execution_id = event["Execution"]["Id"].split(":")[-1]
    return low_level_api(
        s3_client,
        bucket=BUCKET,
        prefix=PREFIX,
        execution_id=execution_id,
        dry_run=False,
    )
