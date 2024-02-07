# -*- coding: utf-8 -*-

import os
import json
import random
import time

import pytest
import requests
from pynamodb.connection import Connection

from simple_lbd_agw_chalice.boto_ses import boto_ses_factory
from simple_lbd_agw_chalice.config.api import config
from simple_lbd_agw_chalice.lbd.add_one import Counter


endpoint = config.env.get_api_gateway_endpoint(bsm_devops=boto_ses_factory.bsm_devops)

headers = {
    "Authorization": config.env.auth_token,
    "Content-Type": "application/json",
}


def _test_hello():
    res = requests.get(f"{endpoint}/", headers=headers)
    assert res.json()["message"] == "Hello World!"


def _test_user():
    res = requests.post(
        f"{endpoint}/user",
        headers=headers,
        data=json.dumps({"name": "alice"}),
    )
    assert res.json()["message"] == "hello alice"


def _test_incr():
    # --------------------------------------------------------------------------
    # Before
    # --------------------------------------------------------------------------
    key = "integration_test_invoke_api"
    try:
        item = Counter.get(key)
        item.delete()
    except Counter.DoesNotExist:
        pass

    # --------------------------------------------------------------------------
    # Invoke
    # --------------------------------------------------------------------------
    n = random.randint(1, 3)
    for _ in range(n):
        res = requests.post(
            f"{endpoint}/incr",
            headers=headers,
            data=json.dumps({"key": key}),
        )
        assert res.json()["message"] == "success"
        assert res.status_code == 200
    time.sleep(1)

    # --------------------------------------------------------------------------
    # After
    # --------------------------------------------------------------------------
    item = Counter.get(key)
    assert item.count == n


def test():
    with boto_ses_factory.bsm.awscli():
        _test_hello()
        _test_user()
        _test_incr()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
