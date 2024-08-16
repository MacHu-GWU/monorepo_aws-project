# -*- coding: utf-8 -*-

from dynamodbsnaplake.lbd.step1_start import lambda_handler as s1_start_handler
from dynamodbsnaplake.lbd.step2_run_job import lambda_handler as s2_run_job_handler
from dynamodbsnaplake.lbd.step3_check_status import (
    lambda_handler as s3_check_status_handler,
)
from dynamodbsnaplake.vendor.parquet_dynamodb.api import (
    Step1CheckAndSetupPrerequisitesRequest,
    Step2RunDynamoDBExportJob,
    Step3RunEtlJobPlanner,
    Step4SnapshotToStagingOrchestrator,
    Step5ProcessDbSnapshotFileGroupManifest,
    Step6StagingToDatalakeOrchestrator,
    Step7ProcessPartitionFileGroupManifest,
    Step8ValidateResults,
)

# fmt: off
step1_check_up_handler = Step1CheckAndSetupPrerequisitesRequest.lambda_handler
step2_run_export_job_handler = Step2RunDynamoDBExportJob.lambda_handler
step3_run_etl_planner_handler =  Step3RunEtlJobPlanner.lambda_handler
step4_run_snap_to_stage_orch_handler = Step4SnapshotToStagingOrchestrator.lambda_handler
step5_run_snap_to_stage_work_handler = Step5ProcessDbSnapshotFileGroupManifest.lambda_handler
step6_run_stage_to_lake_orch_handler = Step6StagingToDatalakeOrchestrator.lambda_handler
step7_run_stage_to_lake_work_handler = Step7ProcessPartitionFileGroupManifest.lambda_handler
step8_validate_results_handler = Step8ValidateResults.lambda_handler
# fmt: on
