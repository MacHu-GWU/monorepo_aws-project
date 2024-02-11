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

        self.stat_s3_bucket_read = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:ListBucket",
                "s3:GetObject",
                "s3:GetObjectAttributes",
                "s3:GetObjectTagging",
            ],
            resources=[
                f"arn:aws:s3:::{self.env.s3dir_env_data.bucket}",
                f"arn:aws:s3:::{self.env.s3dir_env_data.bucket}/{self.env.s3dir_data.key}*",
            ],
        )

        self.stat_s3_bucket_write = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:PutObjectTagging",
                "s3:DeleteObjectTagging",
            ],
            resources=[
                f"arn:aws:s3:::{self.env.s3dir_env_data.bucket}",
                f"arn:aws:s3:::{self.env.s3dir_env_data.bucket}/{self.env.s3dir_data.key}*",
            ],
        )

        self.stat_invoke_lambda = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "lambda:InvokeFunction",
                "lambda:InvokeAsync",
            ],
            resources=["*"],
        )

        # reference: https://docs.aws.amazon.com/step-functions/latest/dg/cw-logs.html#cloudwatch-iam-policy
        self.stat_sfn_cloudwatch_log = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "logs:CreateLogDelivery",
                "logs:CreateLogStream",
                "logs:GetLogDelivery",
                "logs:UpdateLogDelivery",
                "logs:DeleteLogDelivery",
                "logs:ListLogDeliveries",
                "logs:PutLogEvents",
                "logs:PutResourcePolicy",
                "logs:DescribeResourcePolicies",
                "logs:DescribeLogGroups",
            ],
            resources=["*"],
        )

        # lambda function iam role
        self.iam_role_for_lambda = iam.Role(
            self,
            "IamRoleForLambda",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=f"{self.env.prefix_name_snake}-{cdk.Aws.REGION}-lambda",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
            inline_policies={
                f"{self.env.prefix_name_snake}-{cdk.Aws.REGION}-lambda": iam.PolicyDocument(
                    statements=[
                        self.stat_parameter_store,
                        self.stat_s3_bucket_read,
                        self.stat_s3_bucket_write,
                        self.stat_invoke_lambda,
                    ]
                )
            },
        )

        self.output_iam_role_for_lambda_arn = cdk.CfnOutput(
            self,
            "IamRoleForLambdaArn",
            value=self.iam_role_for_lambda.role_arn,
            export_name=f"{self.env.prefix_name_slug}-lambda-role-arn",
        )

        # state machine iam role
        self.iam_role_for_sfn = iam.Role(
            self,
            "IamRoleForSFN",
            assumed_by=iam.ServicePrincipal("states.amazonaws.com"),
            role_name=f"{self.env.prefix_name_snake}-{cdk.Aws.REGION}-sfn",
            inline_policies={
                f"{self.env.prefix_name_snake}-{cdk.Aws.REGION}-sfn": iam.PolicyDocument(
                    statements=[
                        self.stat_invoke_lambda,
                        self.stat_sfn_cloudwatch_log,
                    ]
                )
            },
        )

        self.output_iam_role_for_sfn_arn = cdk.CfnOutput(
            self,
            "IamRoleForSFNArn",
            value=self.iam_role_for_sfn.role_arn,
            export_name=f"{self.env.prefix_name_slug}-sfn-role-arn",
        )
