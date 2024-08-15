# -*- coding: utf-8 -*-

import typing as T
import aws_cdk as cdk

from aws_cdk import (
    aws_iam as iam,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import MainStack


class ParamMixin:
    def mk_rg0_param(self: "MainStack"):
        """
        IAM related resources.

        Ref:

        - IAM Object quotas: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html#reference_iam-quotas-entities
        """
        self.param_bunnymantech_api_key = cdk.CfnParameter(
            self,
            "ParamBunnymantechAPIKey",
            type="String",
            default="ubcotruvlimyrwwmswlwasdpydzdqzylyljvqvtuuptfedmgyxctjqqizgw",
        )
        self.param_bunnymantech_api_key = cdk.CfnParameter(
            self,
            "ParamStaingS3Uri",
            type="String",
            default="s3://my-staging-bucket/dynamodbsnaplake/",
        )
        self.param_bunnymantech_api_key = cdk.CfnParameter(
            self,
            "ParamDataLakeS3UriList",
            type="String",
            default="s3://my-datalake-bucket/datalake/mydatabase1/,s3://my-datalake-bucket/datalake/mydatabase2/,s3://my-datalake-bucket/datalake/mydatabase3/",
        )
