# -*- coding: utf-8 -*-

import json
from datetime import datetime, timezone
from s3pathlib import S3Path
from boto_session_manager import BotoSesManager

from dynamodbsnaplake.config.load import config
from dynamodbsnaplake.paths import dir_project_root
from dynamodbsnaplake.vendor.parquet_dynamodb.lbd import (
    SfnInput,
)

bsm = BotoSesManager(profile_name="bmt_app_dev_us_east_1")
table_arn = f"arn:aws:dynamodb:us-east-1:{bsm.aws_account_id}:table/aws_s3_dynamodb_data_analysis-example-ecommerce_orders"
export_datetime = datetime(2024, 8, 14, 14, 0, 0, tzinfo=timezone.utc)
export_time = export_datetime.isoformat()
exec_arn = f"arn:aws:states:us-east-1:{bsm.aws_account_id}:execution:sfn-poc:a1b2c3d4-9669-40e1-becc-367b03b553d5"
s3dir_root = S3Path(
    f"s3://{bsm.aws_account_alias}-{bsm.aws_region}-data"
    f"/projects/dynamodbsnaplake/envs/sbx/"
).to_dir()
path_python_module = dir_project_root.joinpath("debug", "workflow_settings.py")
s3path_python_module = s3dir_root.joinpath(path_python_module.name)
s3path_python_module.upload_file(str(path_python_module), overwrite=True, bsm=bsm)
sfn_input = SfnInput(
    table_arn=table_arn,
    export_time=export_time,
    s3uri_staging_dir=s3dir_root.joinpath("staging").to_dir().uri,
    s3uri_database_dir=s3dir_root.joinpath("database").to_dir().uri,
    s3uri_python_module=s3path_python_module.uri,
    sort_by=["update_time"],
    descending=[False],
    s3uri_datalake_override=None,
    extract_record_id_override=None,
    extract_create_time_override=None,
    extract_update_time_override=None,
    extract_partition_keys_override=None,
)

input_data = sfn_input.to_dict()
input_json = json.dumps(input_data, indent=4)
now = datetime.now()
# print(input_json)
bsm.sfn_client.start_execution(
    stateMachineArn=config.env.sm_dynamodbsnaplake_workflow.arn,
    name=now.strftime("%Y-%m-%d-%H-%M-%S"),
    input=json.dumps(input_data,),
)

# sfn_input.download_python_module(s3_client=bsm.s3_client)
# sfn_input.project.connect_dynamodb(bsm=bsm)

# --- reset
# sfn_input.s3_loc.s3dir_staging.delete(bsm=bsm)
# sfn_input.project.task_model_step_0_prepare_db_snapshot_manifest.delete_all()
