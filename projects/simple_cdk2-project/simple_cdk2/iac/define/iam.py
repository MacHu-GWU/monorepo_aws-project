# -*- coding: utf-8 -*-

import typing as T
import aws_cdk as cdk

from aws_cdk import (
    aws_iam as iam,
)

from ...boto_ses import boto_ses_factory
from ...env import EnvNameEnum, detect_current_env
from ..simple_cdk1_exports import StackExports as SimpleCdk1StackExports

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import MainStack


class IamMixin:
    def mk_rg1_iam(self: "MainStack"):
        """
        IAM related resources.

        Ref:

        - IAM Object quotas: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html#reference_iam-quotas-entities
        """
        env_name = detect_current_env()
        # don't create this stack in devops environment, because this stack
        # depends on stacks from other projects that is only available in workload account
        # it is not available in devops account.
        if env_name == EnvNameEnum.devops.value:
            return

        simple_cdk_stack_exports = SimpleCdk1StackExports(env_name=env_name)
        simple_cdk_stack_exports.load(
            boto_ses_factory.get_env_bsm(env_name=env_name).cloudformation_client,
        )

        # **reference a resource created by other project (CDK Stack)**
        iam_managed_policy = iam.ManagedPolicy.from_managed_policy_arn(
            self,
            "IamManagedPolicy",
            managed_policy_arn=simple_cdk_stack_exports.get_iam_managed_policy_dummy_arn(),
        )

        self.iam_role = iam.Role(
            self,
            "IamRole",
            role_name=f"{self.env.prefix_name_snake}-{cdk.Aws.REGION}-dummy",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[iam_managed_policy],
        )

        self.iam_role_dummy_arn = cdk.CfnOutput(
            self,
            "IamRoleDummyArn",
            value=self.iam_role.role_arn,
            export_name=f"{self.env.prefix_name_slug}-dummy-arn",
        )
