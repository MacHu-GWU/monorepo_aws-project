# -*- coding: utf-8 -*-

import typing as T
import aws_cdk as cdk

from aws_cdk import (
    aws_iam as iam,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import MainStack


class IamMixin:
    def mk_rg1_iam(self: "MainStack"):
        """
        IAM related resources.

        Ref:

        - IAM Object quotas: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html#reference_iam-quotas-entities
        """

        self.stat_parameter_store = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["ssm:GetParameter"],
            resources=[
                f"arn:aws:ssm:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:parameter/{self.env.parameter_name}"
            ],
        )

        self.iam_managed_policy_dummy = iam.ManagedPolicy(
            self,
            "IamManagedPolicy",
            managed_policy_name=f"{self.env.prefix_name_snake}-{cdk.Aws.REGION}-dummy",
            document=iam.PolicyDocument(statements=[self.stat_parameter_store]),
        )

        self.iam_managed_policy_dummy_arn = cdk.CfnOutput(
            self,
            "IamManagedPolicyArn",
            value=self.iam_managed_policy_dummy.managed_policy_arn,
            export_name=f"{self.env.prefix_name_slug}-dummy-policy-arn",
        )
