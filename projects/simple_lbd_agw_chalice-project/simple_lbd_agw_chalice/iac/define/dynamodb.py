# -*- coding: utf-8 -*-

import typing as T

import aws_cdk as cdk
from aws_cdk import (
    aws_dynamodb as dynamodb,
)

from ...env import EnvNameEnum

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import MainStack


class DynamodbMixin:
    def mk_rg2_dynamodb(self: "MainStack"):
        if self.env.env_name == EnvNameEnum.prd.value:
            removal_policy = cdk.RemovalPolicy.RETAIN
        else:
            removal_policy = cdk.RemovalPolicy.DESTROY
        self.dynamodb_table_counter = dynamodb.Table(
            self,
            "DynamodbTableCounter",
            table_name=self.env.dynamodb_table_name,
            partition_key=dynamodb.Attribute(
                name="key", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=removal_policy,
        )
