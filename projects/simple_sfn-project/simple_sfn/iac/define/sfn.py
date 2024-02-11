# -*- coding: utf-8 -*-

import typing as T

import aws_cdk as cdk
from aws_cdk import (
    aws_logs as logs,
    aws_stepfunctions as sfn,
)

if T.TYPE_CHECKING:
    from .main import MainStack


class SfnMixin:
    def mk_rg3_sfn(self: "MainStack"):
        self.sfn_run_job_log_group = logs.LogGroup(
            self,
            f"StateMachineLogGroup{self.env.sm_run_job.short_name_camel}",
            log_group_name=self.env.sm_run_job.log_group_name,
        )
        self.sfn_run_job_log_group.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        definition = {
            "Comment": "A description of my state machine",
            "StartAt": "Run Job",
            "States": {
                "Run Job": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                        "Payload.$": "$$",
                        "FunctionName": self.env.lbd_s1_start.name,
                    },
                    "Retry": [
                        {
                            "ErrorEquals": [
                                "Lambda.ServiceException",
                                "Lambda.AWSLambdaException",
                                "Lambda.SdkClientException",
                                "Lambda.TooManyRequestsException",
                            ],
                            "IntervalSeconds": 2,
                            "MaxAttempts": 0,
                            "BackoffRate": 2,
                        }
                    ],
                    "Next": "Wait X Seconds",
                },
                "Wait X Seconds": {
                    "Type": "Wait",
                    "Next": "Get Job Status",
                    "Seconds": 3,
                },
                "Get Job Status": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                        "Payload.$": "$$",
                        "FunctionName": self.env.lbd_s3_check_status.name,
                    },
                    "Retry": [
                        {
                            "ErrorEquals": [
                                "Lambda.ServiceException",
                                "Lambda.AWSLambdaException",
                                "Lambda.SdkClientException",
                                "Lambda.TooManyRequestsException",
                            ],
                            "IntervalSeconds": 2,
                            "MaxAttempts": 0,
                            "BackoffRate": 2,
                        }
                    ],
                    "Next": "Job Complete?",
                },
                "Job Complete?": {
                    "Type": "Choice",
                    "Choices": [
                        {
                            "Variable": "$.status",
                            "StringEquals": "failed",
                            "Next": "Fail",
                        },
                        {
                            "Variable": "$.status",
                            "StringEquals": "succeeded",
                            "Next": "Success",
                        },
                    ],
                    "Default": "Wait X Seconds",
                },
                "Success": {"Type": "Succeed"},
                "Fail": {"Type": "Fail"},
            },
        }

        self.sfn_run_job = sfn.CfnStateMachine(
            self,
            f"StateMachine{self.env.sm_run_job.short_name_camel}",
            role_arn=self.iam_role_for_sfn.role_arn,
            definition=definition,
            state_machine_name=self.env.sm_run_job.name,
            state_machine_type="STANDARD",
            logging_configuration=sfn.CfnStateMachine.LoggingConfigurationProperty(
                destinations=[
                    sfn.CfnStateMachine.LogDestinationProperty(
                        cloud_watch_logs_log_group=sfn.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                            log_group_arn=self.sfn_run_job_log_group.log_group_arn,
                        )
                    )
                ],
                include_execution_data=False,
                level="ALL",
            ),
        )
