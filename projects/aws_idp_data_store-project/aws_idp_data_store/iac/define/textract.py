# -*- coding: utf-8 -*-

import typing as T
import aws_cdk as cdk

from aws_cdk import (
    aws_iam as iam,
    aws_sns as sns,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import MainStack


class TextractMixin:
    def mk_rg2_textract(self: "MainStack"):
        """
        IAM related resources.

        Ref:

        - IAM Object quotas: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html#reference_iam-quotas-entities
        """
        self.sns_topic_for_textract = sns.Topic(
            self,
            "SNSTopicForTextract",
            topic_name=self.env.textract_sns_topic_name,
            fifo=False,
        )
        self.output_sns_topic_arn = cdk.CfnOutput(
            self,
            "SNSTopicForTextractArn",
            value=self.sns_topic_for_textract.topic_arn,
            export_name=f"{self.env.prefix_name_slug}-textract-sns-topic-arn",
        )

        self.stat_sns = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "sns:Publish",
                "sns:GetTopicAttributes",
            ],
            resources=[
                self.sns_topic_for_textract.topic_arn,
            ],
        )

        # declare iam role
        self.iam_role_for_textract = iam.Role(
            self,
            "IamRoleForTextract",
            assumed_by=iam.ServicePrincipal("textract.amazonaws.com"),
            role_name=f"{self.env.prefix_name_snake}-{cdk.Aws.REGION}-textract",
            inline_policies={
                f"{self.env.prefix_name_snake}-{cdk.Aws.REGION}-textract": iam.PolicyDocument(
                    statements=[
                        self.stat_s3_bucket_read,
                        self.stat_s3_bucket_write,
                        self.stat_sns,
                    ]
                )
            },
        )

        self.output_iam_role_for_textracta_arn = cdk.CfnOutput(
            self,
            "IamRoleForTextractArn",
            value=self.iam_role_for_textract.role_arn,
            export_name=f"{self.env.prefix_name_slug}-textract-role-arn",
        )
