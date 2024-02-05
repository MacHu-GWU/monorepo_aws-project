# -*- coding: utf-8 -*-

import pytest
import os
import json
import base64

import aws_console_url.api as aws_console_url

from simple_lbd_agw_chalice.config.load import config
from simple_lbd_agw_chalice.boto_ses import bsm
from simple_lbd_agw_chalice.logger import logger

aws = aws_console_url.AWSConsole.from_bsm(bsm)


def _test():
    # test case 1
    payload = {"name": "bob"}
    response = bsm.lambda_client.invoke(
        FunctionName=config.env.lbd_hello.name,
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=json.dumps(payload),
    )
    request_id = response["ResponseMetadata"]["RequestId"]
    logs_console_url = aws.cloudwatch.filter_log_event_by_lambda_request_id(
        func_name=config.env.lbd_hello.name,
        request_id=request_id,
    )
    logger.info(f"preview lambda logs: {logs_console_url}")

    log = base64.b64decode(response["LogResult"].encode("utf-8")).decode("utf-8")
    result: dict = json.loads(response["Payload"].read().decode("utf-8"))
    assert result["message"] == "hello bob"

    # test case 2
    payload = {}
    response = bsm.lambda_client.invoke(
        FunctionName=config.env.lbd_hello.name,
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=json.dumps(payload),
    )
    request_id = response["ResponseMetadata"]["RequestId"]
    logs_console_url = aws.cloudwatch.filter_log_event_by_lambda_request_id(
        func_name=config.env.lbd_hello.name,
        request_id=request_id,
    )
    logger.info(f"preview lambda logs: {logs_console_url}")
    log = base64.b64decode(response["LogResult"].encode("utf-8")).decode("utf-8")
    result: dict = json.loads(response["Payload"].read().decode("utf-8"))

    # print(log)
    assert result["message"] == "hello Mr X"


def test():
    print("")
    with logger.disabled(
        disable=True,
        # disable=False,
    ):
        _test()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
