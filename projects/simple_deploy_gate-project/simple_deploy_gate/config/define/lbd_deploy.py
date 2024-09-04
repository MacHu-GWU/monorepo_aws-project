# -*- coding: utf-8 -*-

"""
Lambda function deployment related configurations.
"""

import typing as T
import json
import dataclasses

from s3pathlib import S3Path

if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager
    from .main import Env


@dataclasses.dataclass
class LambdaDeployMixin:
    """
    Lambda function deployment related configurations.
    """

    @property
    def chalice_app_name(self: "Env") -> str:
        """
        If you use AWS Chalice framework to deploy your lambda function,
        it is the chalice app name.

        See more details at: https://aws.github.io/chalice/?badge=latest
        """
        return self.project_name_snake

    @property
    def lambda_layer_name(self: "Env") -> str:
        """
        Lambda function layer name.

        Because the Lambda layer is an immutable artifact, we only need one
        lambda layer across all envs, so we don't need to include env name in the
        layer name.
        """
        return self.project_name_snake

    @property
    def s3dir_lambda(self: "Env") -> S3Path:
        """
        Where you store lambda related artifacts.

        example: ``${s3dir_artifacts}/lambda/``
        """
        return self.s3dir_artifacts.joinpath("lambda").to_dir()

    @property
    def s3dir_deployed(self: "Env") -> S3Path:
        """
        `AWS Chalice <https://aws.github.io/chalice/>`_ use ``deployed.json``
        to store the deployed resources. It is better to store all of
        historical ``deployed.json`` files somewhere as a record.

        example: ``${s3dir_artifacts}/lambda/deployed/``
        """
        return self.s3dir_lambda.joinpath("deployed").to_dir()

    @property
    def s3path_deployed_json(self: "Env") -> S3Path:
        """
        AWS Chalice deployed resources JSON file.

        example: ``${s3dir_artifacts}/lambda/deployed/${env_name}.json``
        """
        return self.s3dir_deployed.joinpath(f"{self.env_name}.json")

    def get_api_gateway_endpoint(
        self: "Env",
        bsm_devops: "BotoSesManager",
    ) -> str:  # pragma: no cover
        """
        Get current environment rest API endpoint.

        :return: example ``https://a1b2c3d4.execute-api.us-east-1.amazonaws.com/api``
        """
        data = json.loads(self.s3path_deployed_json.read_text(bsm=bsm_devops))
        mapper = {dct["name"]: dct for dct in data.get("resources", [])}
        endpoint = mapper["rest_api"]["rest_api_url"]
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        return endpoint

    def endpoint_to_rest_api_id(self, endpoint: str) -> str:
        return endpoint.split("/")[2].split(".")[0]
