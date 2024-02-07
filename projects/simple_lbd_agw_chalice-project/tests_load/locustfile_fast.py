# -*- coding: utf-8 -*-

import json
from locust import task, FastHttpUser, constant
from simple_lbd_agw_chalice.boto_ses import boto_ses_factory
from simple_lbd_agw_chalice.config.api import config

# make sure it ends with /
endpoint = config.env.get_api_gateway_endpoint(bsm_devops=boto_ses_factory.bsm_devops)
if not endpoint.endswith("/"):
    endpoint += "/"

# HTTP header for authentication and other purpose
headers = {
    "Authorization": config.env.auth_token,
    "Content-Type": "application/json",
}


# A coroutine, non blocker, async, high concurrent HTTP client
class FastUser(FastHttpUser):
    # since you defined the host, you can use relative path in your task
    host = endpoint

    # add 1 sec delay for all user. once one task is fired, it wait 1 sec to
    # fire another one
    wait_time = constant(1)

    @task
    def call_api(self):
        response = self.client.post(
            "incr",
            headers=headers,
            data=json.dumps({"key": "test"}),
        )
        # print(response.text)
