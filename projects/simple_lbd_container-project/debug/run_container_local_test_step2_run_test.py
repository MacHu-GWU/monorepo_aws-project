# -*- coding: utf-8 -*-

"""
Send custom event to local lambda container.

Reference:

- Using an AWS base image for Python - (Optional) Test the image locally: https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions
"""

import json

import requests
from simple_lbd_container.config.define.lbd_func import LambdaFunction
from simple_lbd_container.config.api import config


def run_lambda_container(
    lbd_func: LambdaFunction,
    event: dict = None,
):
    """
    Send HTTP POST request to the local lambda container.

    Equivalent to::

        curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"handler": "hello_handler", "event": {"name": "john"}}'
    """
    url = "http://localhost:9000/2015-03-31/functions/function/invocations"
    if event is None:
        event = {}
    data = {
        "handler": lbd_func.handler,
        "event": event,
    }
    print(f"request.data: ")
    print(json.dumps(data, indent=4))
    response = requests.post(url, data=json.dumps(data))
    print(f"response.status_code = {response.status_code}")
    print(f"response.headers = {response.headers}")
    print(f"response.text = ")
    print(json.dumps(json.loads(response.text), indent=4))


if __name__ == "__main__":
    # choose which lambda function to invoke
    lbd_func = config.env.lbd_hello
    # put event data here
    event = {}
    # run it
    run_lambda_container(lbd_func=lbd_func, event=event)
