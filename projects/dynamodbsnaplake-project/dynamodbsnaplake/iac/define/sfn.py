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
        self.sfn_dynamodbsnaplake_workflow_log_group = logs.LogGroup(
            self,
            f"StateMachineLogGroup{self.env.sm_dynamodbsnaplake_workflow.short_name_camel}",
            log_group_name=self.env.sm_dynamodbsnaplake_workflow.log_group_name,
        )
        self.sfn_dynamodbsnaplake_workflow_log_group.apply_removal_policy(
            cdk.RemovalPolicy.DESTROY
        )

        definition = {
            "Comment": "A description of my state machine",
            "StartAt": "Step 1 - Check and Setup Prerequisites",
            "States": {
                "Step 1 - Check and Setup Prerequisites": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                        "Payload": {
                            "exec_arn.$": "$$.Execution.Id",
                            "sfn_input.$": "$$.Execution.Input",
                        },
                        "FunctionName": self.env.lbd_step1_check_up.name,
                    },
                    "Retry": [
                        {
                            "ErrorEquals": [
                                "Lambda.ServiceException",
                                "Lambda.AWSLambdaException",
                                "Lambda.SdkClientException",
                                "Lambda.TooManyRequestsException",
                            ],
                            "IntervalSeconds": 1,
                            "MaxAttempts": 3,
                            "BackoffRate": 2,
                        }
                    ],
                    "Next": "Step 2 - Run DynamoDB Export Job if not Exists",
                    "Comment": "1. Check if S3 bucket is setup property\n2. Check if the S3 staging location is empty\n3. Check if the S3 datalake location is empty\n4. Check if the DynamoDB function is ready",
                },
                "Step 2 - Run DynamoDB Export Job if not Exists": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                        "Payload": {
                            "exec_arn.$": "$$.Execution.Id",
                            "sfn_input.$": "$$.Execution.Input",
                        },
                        "FunctionName": self.env.lbd_step2_run_export_job.name,
                    },
                    "Retry": [
                        {
                            "ErrorEquals": [
                                "Lambda.ServiceException",
                                "Lambda.AWSLambdaException",
                                "Lambda.SdkClientException",
                                "Lambda.TooManyRequestsException",
                            ],
                            "IntervalSeconds": 1,
                            "MaxAttempts": 3,
                            "BackoffRate": 2,
                        }
                    ],
                    "Next": "Get Export Job Status",
                    "Comment": "If the DynamoDB export run never executed before, run DynamoDB export.",
                },
                "Get Export Job Status": {
                    "Type": "Task",
                    "Parameters": {"ExportArn.$": "$.ExportDescription.ExportArn"},
                    "Resource": "arn:aws:states:::aws-sdk:dynamodb:describeExport",
                    "Next": "Export Job succeeded?",
                },
                "Wait X Seconds": {
                    "Type": "Wait",
                    "Seconds": 30,
                    "Next": "Get Export Job Status",
                },
                "Export Job succeeded?": {
                    "Type": "Choice",
                    "Choices": [
                        {
                            "Variable": "$.ExportDescription.ExportStatus",
                            "StringEquals": "FAILED",
                            "Next": "Fail",
                        },
                        {
                            "Variable": "$.ExportDescription.ExportStatus",
                            "StringEquals": "COMPLETED",
                            "Next": "Step 3 - Run ETL Job Planner",
                        },
                    ],
                    "Default": "Wait X Seconds",
                },
                "Step 3 - Run ETL Job Planner": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                        "Payload": {
                            "exec_arn.$": "$$.Execution.Id",
                            "sfn_input.$": "$$.Execution.Input",
                        },
                        "FunctionName": self.env.lbd_step3_run_etl_planner.name,
                    },
                    "Retry": [
                        {
                            "ErrorEquals": [
                                "Lambda.ServiceException",
                                "Lambda.AWSLambdaException",
                                "Lambda.SdkClientException",
                                "Lambda.TooManyRequestsException",
                            ],
                            "IntervalSeconds": 1,
                            "MaxAttempts": 3,
                            "BackoffRate": 2,
                        }
                    ],
                    "Next": "Step 4 - Generate Many DB Snapshot File Group Manifest and dispatch to Workers",
                    "Comment": "Analyze the DynamoDB export data and determine the optimal batch size for each concurrent worker. Also, generate the DB Snapshot File Manifest File.",
                },
                "Step 4 - Generate Many DB Snapshot File Group Manifest and dispatch to Workers": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                        "Payload": {
                            "exec_arn.$": "$$.Execution.Id",
                            "sfn_input.$": "$$.Execution.Input",
                        },
                        "FunctionName": self.env.lbd_step4_run_snap_to_stage_orch.name,
                    },
                    "Retry": [
                        {
                            "ErrorEquals": [
                                "Lambda.ServiceException",
                                "Lambda.AWSLambdaException",
                                "Lambda.SdkClientException",
                                "Lambda.TooManyRequestsException",
                            ],
                            "IntervalSeconds": 1,
                            "MaxAttempts": 3,
                            "BackoffRate": 2,
                        }
                    ],
                    "Next": "Dispatch DB Snapshot File Group Manifest to Workers",
                },
                "Dispatch DB Snapshot File Group Manifest to Workers": {
                    "Type": "Map",
                    "ItemProcessor": {
                        "ProcessorConfig": {
                            "Mode": "DISTRIBUTED",
                            "ExecutionType": "STANDARD",
                        },
                        "StartAt": "Step 5 - Process DB Snapshot File Group Manifest",
                        "States": {
                            "Step 5 - Process DB Snapshot File Group Manifest": {
                                "Type": "Task",
                                "Resource": "arn:aws:states:::lambda:invoke",
                                "OutputPath": "$.Payload",
                                "Parameters": {
                                    "Payload.$": "$",
                                    "FunctionName": self.env.lbd_step5_run_snap_to_stage_work.name,
                                },
                                "Retry": [
                                    {
                                        "ErrorEquals": [
                                            "Lambda.ServiceException",
                                            "Lambda.AWSLambdaException",
                                            "Lambda.SdkClientException",
                                            "Lambda.TooManyRequestsException",
                                        ],
                                        "IntervalSeconds": 1,
                                        "MaxAttempts": 3,
                                        "BackoffRate": 2,
                                    }
                                ],
                                "End": True,
                            }
                        },
                    },
                    "Label": "SnapshotToStagingWorkers",
                    "MaxConcurrency": 100,
                    "Next": "Step 6 - Generate Partition File Group Manifest and Dispatch to Workers",
                    "ItemReader": {
                        "Resource": "arn:aws:states:::s3:getObject",
                        "ReaderConfig": {"InputType": "JSON"},
                        "Parameters": {
                            "Bucket.$": "$.map_payload_bucket",
                            "Key.$": "$.map_payload_key",
                        },
                    },
                },
                "Step 6 - Generate Partition File Group Manifest and Dispatch to Workers": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                        "Payload": {
                            "exec_arn.$": "$$.Execution.Id",
                            "sfn_input.$": "$$.Execution.Input",
                        },
                        "FunctionName": self.env.lbd_step6_run_stage_to_lake_orch.name,
                    },
                    "Retry": [
                        {
                            "ErrorEquals": [
                                "Lambda.ServiceException",
                                "Lambda.AWSLambdaException",
                                "Lambda.SdkClientException",
                                "Lambda.TooManyRequestsException",
                            ],
                            "IntervalSeconds": 1,
                            "MaxAttempts": 3,
                            "BackoffRate": 2,
                        }
                    ],
                    "Next": "Dispatch Partition File Group Manifest to Workers",
                },
                "Dispatch Partition File Group Manifest to Workers": {
                    "Type": "Map",
                    "ItemProcessor": {
                        "ProcessorConfig": {
                            "Mode": "DISTRIBUTED",
                            "ExecutionType": "STANDARD",
                        },
                        "StartAt": "Step 7 - Process Partition File Group Manifest",
                        "States": {
                            "Step 7 - Process Partition File Group Manifest": {
                                "Type": "Task",
                                "Resource": "arn:aws:states:::lambda:invoke",
                                "OutputPath": "$.Payload",
                                "Parameters": {
                                    "Payload.$": "$",
                                    "FunctionName": self.env.lbd_step7_run_stage_to_lake_work.name,
                                },
                                "Retry": [
                                    {
                                        "ErrorEquals": [
                                            "Lambda.ServiceException",
                                            "Lambda.AWSLambdaException",
                                            "Lambda.SdkClientException",
                                            "Lambda.TooManyRequestsException",
                                        ],
                                        "IntervalSeconds": 1,
                                        "MaxAttempts": 3,
                                        "BackoffRate": 2,
                                    }
                                ],
                                "End": True,
                            }
                        },
                    },
                    "Next": "Step 8 - Validate Results",
                    "Label": "StagingToDatalakeWorkers",
                    "MaxConcurrency": 100,
                    "ItemReader": {
                        "Resource": "arn:aws:states:::s3:getObject",
                        "ReaderConfig": {"InputType": "JSON"},
                        "Parameters": {
                            "Bucket.$": "$.map_payload_bucket",
                            "Key.$": "$.map_payload_key",
                        },
                    },
                },
                "Step 8 - Validate Results": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                        "Payload": {
                            "exec_arn.$": "$$.Execution.Id",
                            "sfn_input.$": "$$.Execution.Input"
                        }
                    },
                    "Retry": [
                        {
                            "ErrorEquals": [
                                "Lambda.ServiceException",
                                "Lambda.AWSLambdaException",
                                "Lambda.SdkClientException",
                                "Lambda.TooManyRequestsException"
                            ],
                            "IntervalSeconds": 1,
                            "MaxAttempts": 3,
                            "BackoffRate": 2
                        }
                    ],
                    "Next": "Success"
                },
                "Success": {"Type": "Succeed"},
                "Fail": {"Type": "Fail"},
            },
        }
        # import json
        # from pathlib import Path
        # path = Path("/Users/sanhehu/Documents/GitHub/monorepo_aws-project/projects/dynamodbsnaplake-project/debug/sfn_debug.json")
        # path.write_text(json.dumps(definition, indent=4))

        self.sfn_dynamodbsnaplake_workflow = sfn.CfnStateMachine(
            self,
            f"StateMachine{self.env.sm_dynamodbsnaplake_workflow.short_name_camel}",
            role_arn=self.iam_role_for_sfn.role_arn,
            definition=definition,
            state_machine_name=self.env.sm_dynamodbsnaplake_workflow.name,
            state_machine_type="STANDARD",
            logging_configuration=sfn.CfnStateMachine.LoggingConfigurationProperty(
                destinations=[
                    sfn.CfnStateMachine.LogDestinationProperty(
                        cloud_watch_logs_log_group=sfn.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                            log_group_arn=self.sfn_dynamodbsnaplake_workflow_log_group.log_group_arn,
                        )
                    )
                ],
                include_execution_data=False,
                level="ALL",
            ),
        )
