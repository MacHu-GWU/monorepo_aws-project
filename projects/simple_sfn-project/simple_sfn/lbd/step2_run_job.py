# -*- coding: utf-8 -*-

"""
This job takes 5 - 15 seconds to finish.

It has 30% chance to fail
"""

import os
import time
import json
import random

import boto3

from .common import JobStatus
from ..logger import logger

PROJECT_NAME = os.environ.get("PROJECT_NAME")
ENV_NAME = os.environ.get("ENV_NAME")
BUCKET = os.environ.get("BUCKET")
PREFIX = os.environ.get("PREFIX")

s3_client = boto3.client("s3")


def low_level_api(
    s3_client,
    bucket: str,
    prefix: str,
    execution_id: str,
    instant_finish: bool = False,
    always_succeed: bool = False,
) -> dict:
    """
    Simulate a long-running job. It takes 5 - 15 seconds to finish,
    and has 70% chance to succeed.
    """
    if prefix.endswith("/"):
        prefix = prefix[:-1]

    def write_status(status: str):
        JobStatus.write(
            s3_client=s3_client,
            bucket=bucket,
            prefix=prefix,
            exec_id=execution_id,
            status=status,
        )

    write_status(JobStatus.running)
    if instant_finish:
        elapse = 0.001
    else:
        elapse = random.randint(5, 15)
    time.sleep(elapse)
    if always_succeed:
        succeeded_flag = True
    else:
        succeeded_flag = random.randint(1, 100) <= 70
    if succeeded_flag:
        write_status(JobStatus.succeeded)
        return {"message": f"succeeded in {elapse} seconds"}
    else:
        write_status(JobStatus.failed)
        raise ValueError("job failed!")


@logger.start_and_end(
    msg="{func_name}",
)
def lambda_handler(event, context):  # pragma: no cover
    logger.info("received event:")
    logger.info(json.dumps(event, indent=4))
    execution_id = event["exec_id"]
    return low_level_api(
        s3_client=s3_client,
        bucket=BUCKET,
        prefix=PREFIX,
        execution_id=execution_id,
    )
