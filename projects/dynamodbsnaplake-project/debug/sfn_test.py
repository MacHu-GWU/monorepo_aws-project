# -*- coding: utf-8 -*-

"""
This script run an end to end test of the DynamoDB Snapshot to Datalake workflow.
"""

import json
from datetime import datetime
from s3pathlib import S3Path
from boto_session_manager import BotoSesManager

from dynamodbsnaplake.config.load import config
from dynamodbsnaplake.paths import dir_project_root
from dynamodbsnaplake.vendor.parquet_dynamodb.lbd import (
    SfnInput,
)

# ------------------------------------------------------------------------------
# Enter your test settings here.
# ------------------------------------------------------------------------------
aws_profile = "bmt_app_dev_us_east_1"
dynamodb_table_name = "aws_s3_dynamodb_data_analysis-example-ecommerce_orders"
export_time_str = "2024-08-14T16:00:00+00:00"
reset_data = True
reset_tracker = True


# ------------------------------------------------------------------------------
# Don't change anything below this line.
# ------------------------------------------------------------------------------
bsm = BotoSesManager(profile_name=aws_profile)
dynamodb_table_arn = f"arn:aws:dynamodb:{bsm.aws_region}:{bsm.aws_account_id}:table/{dynamodb_table_name}"
export_datetime = datetime.fromisoformat(export_time_str)
bucket = f"{bsm.aws_account_alias}-{bsm.aws_region}-data"
s3dir_root = S3Path(f"s3://{bucket}/projects/dynamodbsnaplake/envs/sbx/").to_dir()
s3uri_staging_dir = s3dir_root.joinpath("staging").to_dir().uri
s3uri_database_dir = s3dir_root.joinpath("database").to_dir().uri
# See this python module at
# https://github.com/MacHu-GWU/monorepo_aws-project/blob/main/projects/dynamodbsnaplake-project/debug/workflow_settings.py
path_python_module = dir_project_root.joinpath("debug", "workflow_settings.py")
s3path_python_module = s3dir_root.joinpath(path_python_module.name)
s3path_python_module.write_text(
    path_python_module.read_text(),
    content_type="text/plain",
    bsm=bsm,
)
print(f"{s3path_python_module.uri = }")
print(f"{s3path_python_module.console_url = }")

# Create the most-important StepFunction input object
sfn_input = SfnInput(
    table_arn=dynamodb_table_arn,
    export_time=export_time_str,
    s3uri_staging_dir=s3uri_staging_dir,
    s3uri_database_dir=s3uri_database_dir,
    s3uri_python_module=s3path_python_module.uri,
    sort_by=["update_time"],
    descending=[False],
    count_on_column="OrderID",
    s3uri_datalake_override=None,
    extract_record_id_override=None,
    extract_create_time_override=None,
    extract_update_time_override=None,
    extract_partition_keys_override=None,
)
input_data = sfn_input.to_dict()
print(input_data)
input_json = json.dumps(input_data, indent=4)
print(input_json)

sfn_input.download_python_module(s3_client=bsm.s3_client)
# reset data and tracker if needed
if reset_data:
    sfn_input.s3_loc.s3dir_staging.delete(bsm=bsm)
    sfn_input.s3_loc.s3dir_datalake.delete(bsm=bsm)
if reset_tracker:
    sfn_input.project.task_model_step_0_prepare_db_snapshot_manifest.delete_all()

now = datetime.now()
exec_name = now.strftime("%Y-%m-%d-%H-%M-%S")
bsm.sfn_client.start_execution(
    stateMachineArn=config.env.sm_dynamodbsnaplake_workflow.arn,
    name=exec_name,
    input=input_json,
)
