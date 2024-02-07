# -*- coding: utf-8 -*-

"""
This module provides an interface for external code to get the API gateway endpoint.
You can just copy and paste this file into the external codebase.

.. code-block:: python

    >>> import boto3
    >>> s3_client = boto3.client("s3")
    >>> endpoint = get_api_endpoint(env_name="sbx", s3_client=s3_client)
"""

import json

# this value has to match the ``config.project_name``
project_name = "simple_lbd_agw_chalice"
project_name_snake = project_name.replace("-", "_")
project_name_slug = project_name.replace("_", "-")
# this value has to match the ``config.s3uri_artifacts``
artifacts_bucket = "bmt-app-devops-us-east-1-artifacts"


def _get_s3_key(env_name: str) -> str:
    return f"projects/monorepo_aws/{project_name}/lambda/deployed/{env_name}.json"


def get_api_endpoint(env_name: str, s3_client) -> str:
    """
    Get the API endpoint from the chalice deployed ${env_name}.json file in
    artifacts S3 bucket.

    :return: example ``https://a1b2c3d4.execute-api.us-east-1.amazonaws.com/api``
    """
    res = s3_client.get_object(Bucket=artifacts_bucket, Key=_get_s3_key(env_name))
    data = json.loads(res["Body"].read().decode("utf-8"))
    mapper = {dct["name"]: dct for dct in data.get("resources", [])}
    endpoint = mapper["rest_api"]["rest_api_url"]
    if endpoint.endswith("/"):
        endpoint = endpoint[:-1]
    return endpoint
