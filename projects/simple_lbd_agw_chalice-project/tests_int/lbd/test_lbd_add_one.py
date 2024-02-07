# -*- coding: utf-8 -*-

import pytest
import os
import json
import base64

from pynamodb.connection import Connection
import aws_console_url.api as aws_console_url

from simple_lbd_agw_chalice.config.load import config
from simple_lbd_agw_chalice.logger import logger
from simple_lbd_agw_chalice.boto_ses import bsm
from simple_lbd_agw_chalice.lbd.add_one import Counter


def _test():
    Connection()
    # --------------------------------------------------------------------------
    # before
    # --------------------------------------------------------------------------

    key = "integration_test_invoke_api"
    try:
        item = Counter.get(key)
        item.delete()
    except Counter.DoesNotExist:
        pass

    # --------------------------------------------------------------------------
    # invoke
    # --------------------------------------------------------------------------
    response = bsm.lambda_client.invoke(
        FunctionName=config.env.lbd_add_one.name,
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=json.dumps({"key": key}),
    )
    request_id = response["ResponseMetadata"]["RequestId"]
    aws_console = aws_console_url.AWSConsole.from_bsm(bsm)
    logs_console_url = aws_console.cloudwatch.filter_log_event_by_lambda_request_id(
        func_name=config.env.lbd_hello.name,
        request_id=request_id,
    )
    logger.info(f"preview lambda logs: {logs_console_url}")

    log = base64.b64decode(response["LogResult"].encode("utf-8")).decode("utf-8")
    result: dict = json.loads(response["Payload"].read().decode("utf-8"))

    # --------------------------------------------------------------------------
    # after
    # --------------------------------------------------------------------------
    item = Counter.get(key)
    assert item.count == 1
    assert result["message"] == "success"


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
