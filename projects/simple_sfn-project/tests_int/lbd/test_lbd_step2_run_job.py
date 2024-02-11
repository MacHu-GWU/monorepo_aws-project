# -*- coding: utf-8 -*-

import pytest
import os
import json
import uuid
import base64

import aws_console_url.api as aws_console_url

from simple_sfn.config.api import config
from simple_sfn.boto_ses import bsm
from simple_sfn.logger import logger
from simple_sfn.lbd.common import JobStatus


aws = aws_console_url.AWSConsole.from_bsm(bsm)


def _test():
    # test case 1
    exec_id = uuid.uuid4().hex
    payload = {"exec_id": exec_id}

    response = bsm.lambda_client.invoke(
        FunctionName=config.env.lbd_s2_run_job.name,
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=json.dumps(payload),
    )
    request_id = response["ResponseMetadata"]["RequestId"]
    logs_console_url = aws.cloudwatch.filter_log_event_by_lambda_request_id(
        func_name=config.env.lbd_s2_run_job.name,
        request_id=request_id,
    )
    logger.info(f"preview lambda logs: {logs_console_url}")

    log = base64.b64decode(response["LogResult"].encode("utf-8")).decode("utf-8")
    result_text: str = response["Payload"].read().decode("utf-8")
    result: dict = json.loads(result_text)
    job_status = JobStatus.read(
        s3_client=bsm.s3_client,
        bucket=config.env.s3dir_sfn_executions.bucket,
        prefix=config.env.s3dir_sfn_executions.key,
        exec_id=exec_id,
    )
    if "Traceback" in log:
        assert job_status == JobStatus.failed
        assert "stackTrace" in result
    else:
        assert job_status == JobStatus.succeeded
        assert "succeeded in " in result["message"]


def test():
    print("")
    with logger.disabled(
        disable=True,  # mute log
        # disable=False,  # show log
    ):
        _test()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
