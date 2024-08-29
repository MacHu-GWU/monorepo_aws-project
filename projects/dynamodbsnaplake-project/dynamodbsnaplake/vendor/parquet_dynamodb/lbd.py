# -*- coding: utf-8 -*-

"""
This module implement the AWS Lambda Function in two ways:

1. :class:`Request` dataclass is a container to hold all the necessary parameter
    for the Lambda Function to run. The :meth:`Request.main` method execute the
    main logic of the Lambda Function. It also can be used for local testing
    without using real AWS Lambda Function.
2. :meth:`Request.lambda_handler` is the entry point for the AWS Lambda Function.
    It reads data from the event, create a :class:`Request` object, and call the
    :meth:`Request.main` method.
"""

import typing as T
import os
import enum
import json
import dataclasses

import botocore.exceptions
from s3pathlib import S3Path
from boto_session_manager import BotoSesManager
from s3manifesto.api import KeyEnum
from dbsnaplake.api import (
    DBSnapshotManifestFile,
    DBSnapshotFileGroupManifestFile,
    PartitionFileGroupManifestFile,
    logger,
    step_1_3_process_db_snapshot_file_group_manifest_file,
    step_2_3_process_partition_file_group_manifest_file,
)
from .sfn_input import SfnInput
from .sfn_ctx import SfnCtx

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client
    from mypy_boto3_dynamodb.client import DynamoDBClient


class RequestTypeEnum(str, enum.Enum):
    # fmt: off
    step1_check_and_setup_prerequisites = "step1_check_and_setup_prerequisites"
    step2_run_dynamodb_export_job = "step2_run_dynamodb_export_job"
    step3_run_etl_job_planner = "step3_run_etl_job_planner"
    step4_generate_many_db_snapshot_file_group_manifest_and_dispatch_to_workers = "step4_generate_many_db_snapshot_file_group_manifest_and_dispatch_to_workers"
    step5_process_db_snapshot_file_group_manifest = "step5_process_db_snapshot_file_group_manifest"
    step6_generate_partition_file_group_manifest_and_dispatch_to_workers = "step6_generate_partition_file_group_manifest_and_dispatch_to_workers"
    step7_process_partition_file_group_manifest = "step7_process_partition_file_group_manifest"
    step8_validate_results = "step8_validate_results"
    # fmt: on


@dataclasses.dataclass
class Request:
    """
    Base class for all the Lambda Function Request dataclass.

    :param bsm: Boto3 Session Manager.
    :param exec_arn: ARN of the Step Function Execution.
    :param sfn_input: The :class:`input data <parquet_dynamodb.sfn_input.SfnInput>`
        for the Step Function.
    """

    bsm: "BotoSesManager" = dataclasses.field()
    exec_arn: str = dataclasses.field()
    sfn_input: SfnInput = dataclasses.field()

    def get_sfn_ctx(self) -> SfnCtx:  # pragma: no cover
        return SfnCtx.read(
            s3_client=self.bsm.s3_client,
            exec_arn=self.exec_arn,
            s3dir_uri=self.sfn_input.s3dir_sfn_ctx.uri,
        )

    def to_dict(self):  # pragma: no cover
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, dct: T.Dict[str, T.Any]):  # pragma: no cover
        raise NotImplementedError

    def main(self):  # pragma: no cover
        raise NotImplementedError

    def lambda_handler(self, event: dict, context):  # pragma: no cover
        raise NotImplementedError


def create_s3_bucket_if_not_exists(
    s3_client: "S3Client",
    bucket: str,
    region: str,
):
    try:
        s3_client.head_bucket(Bucket=bucket)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            kwargs = {"Bucket": bucket}
            if region != "us-east-1":
                kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}
            s3_client.create_bucket(**kwargs)
        else:
            raise e


def ensure_s3_bucket_versioning_is_off(
    s3_client: "S3Client",
    bucket: str,
):
    try:
        res = s3_client.get_bucket_versioning(Bucket=bucket)
        if "Status" in res:
            if res["Status"] != "Disabled":
                raise ValueError(f"you cannot turn on Bucket versioning at: {bucket!r}")
    except botocore.exceptions.ClientError as e:
        raise e


def ensure_dynamodb_table_exists(
    dynamodb_client: "DynamoDBClient",
    table_name: str,
):
    try:
        dynamodb_client.describe_table(TableName=table_name)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            raise ValueError(f"Table does not exist: {table_name!r}")
        else:
            raise e


def turn_on_dynamodb_table_pitr_if_not(
    dynamodb_client: "DynamoDBClient",
    table_name: str,
):
    try:
        res = dynamodb_client.describe_continuous_backups(TableName=table_name)
        if (
            res["ContinuousBackupsDescription"]["PointInTimeRecoveryDescription"][
                "PointInTimeRecoveryStatus"
            ]
            != "ENABLED"
        ):
            dynamodb_client.update_continuous_backups(
                TableName=table_name,
                PointInTimeRecoverySpecification={"PointInTimeRecoveryEnabled": True},
            )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ContinuousBackupsUnavailableException":
            raise ValueError(f"PITR is not available for table: {table_name!r}")
        else:
            raise e


@dataclasses.dataclass
class Step1CheckAndSetupPrerequisitesRequest(Request):
    """
    :param aws_region: if necessary bucket doesn't exists, where to create those
        buckets.
    """

    aws_region: str = dataclasses.field()

    @logger.start_and_end(
        msg="Check and Setup Prerequisites",
    )
    def main(self):
        create_s3_bucket_if_not_exists(
            s3_client=self.bsm.s3_client,
            bucket=self.sfn_input.s3_loc.s3dir_staging.bucket,
            region=self.aws_region,
        )
        create_s3_bucket_if_not_exists(
            s3_client=self.bsm.s3_client,
            bucket=self.sfn_input.s3_loc.s3dir_datalake.bucket,
            region=self.aws_region,
        )
        ensure_s3_bucket_versioning_is_off(
            s3_client=self.bsm.s3_client,
            bucket=self.sfn_input.s3_loc.s3dir_staging.bucket,
        )
        ensure_s3_bucket_versioning_is_off(
            s3_client=self.bsm.s3_client,
            bucket=self.sfn_input.s3_loc.s3dir_datalake.bucket,
        )
        ensure_dynamodb_table_exists(
            dynamodb_client=self.bsm.dynamodb_client,
            table_name=self.sfn_input.table_name,
        )
        turn_on_dynamodb_table_pitr_if_not(
            dynamodb_client=self.bsm.dynamodb_client,
            table_name=self.sfn_input.table_name,
        )

    @classmethod
    def lambda_handler(cls, event: dict, context):  # pragma: no cover
        aws_region = os.environ["AWS_DEFAULT_REGION"]
        bsm = BotoSesManager(region_name=aws_region)
        exec_arn = event["exec_arn"]
        sfn_input = SfnInput(**event["sfn_input"])
        sfn_ctx = SfnCtx(
            exec_arn=event["exec_arn"],
            data=event["sfn_input"],
        )
        sfn_ctx.write(s3_client=bsm.s3_client, s3dir_uri=sfn_input.s3dir_sfn_ctx.uri)
        request = cls(
            bsm=bsm,
            exec_arn=exec_arn,
            sfn_input=sfn_input,
            aws_region=aws_region,
        )
        return request.main()


@dataclasses.dataclass
class Step2RunDynamoDBExportJob(Request):
    """
    todo: add docstring
    """
    @logger.start_and_end(
        msg="Run DynamoDB Export Job",
    )
    def main(self):
        logger.info("Check if we already launched the export job ...")
        export_job, is_already_launched = self.sfn_input.run_or_get_dynamodb_export(
            s3_client=self.bsm.s3_client,
            dynamodb_client=self.bsm.dynamodb_client,
        )
        if is_already_launched is False:
            logger.info("  We never launched the export job, now launch a new one.")
        else:
            logger.info("  We already launched the export job.")
        logger.info("Export job details:")
        logger.info(f"  {export_job.arn = }")
        logger.info(f"  {export_job.start_time = }")
        logger.info(f"  {export_job.status = }")
        return {
            "ExportDescription": {
                "ExportArn": export_job.arn,
            }
        }

    @classmethod
    def lambda_handler(cls, event: dict, context):  # pragma: no cover
        aws_region = os.environ["AWS_DEFAULT_REGION"]
        bsm = BotoSesManager(region_name=aws_region)
        exec_arn = event["exec_arn"]
        sfn_input = SfnInput(**event["sfn_input"])
        request = cls(
            bsm=bsm,
            exec_arn=exec_arn,
            sfn_input=sfn_input,
        )
        return request.main()


@dataclasses.dataclass
class Step3RunEtlJobPlanner(Request):
    """
    todo: add docstring
    """
    @logger.start_and_end(
        msg="Run ETL Job Planner",
    )
    def main(self):
        """ """
        logger.info("Verify the DynamoDB export is completed.")
        export_job, is_already_launched = self.sfn_input.run_or_get_dynamodb_export(
            s3_client=self.bsm.s3_client,
            dynamodb_client=self.bsm.dynamodb_client,
        )
        if export_job.is_completed() is False:
            raise ValueError(f"Export job {export_job.arn} is not completed yet.")

        # if self.sfn_input.s3uri_python_module is not None:
        #     self.sfn_input.download_python_module(s3_client=self.bsm.s3_client)
        Task = self.sfn_input.project.task_model_step_0_prepare_db_snapshot_manifest

        task_id = "run_etl_job_planner"
        task = Task.get_one_or_none(task_id=task_id)
        if task is None:
            task = Task.make_and_save(task_id=task_id)
        if task.is_succeeded():
            return

        with Task.start(task_id=task_id, debug=True) as exec_ctx:
            logger.info("Analyze export job manifest data, convert it to DBSnapshotManifestFile format ...")
            manifest_summary = export_job.get_manifest_summary(
                dynamodb_client=self.bsm.dynamodb_client,
                s3_client=self.bsm.s3_client,
            )
            data_file_list = export_job.get_data_files(
                dynamodb_client=self.bsm.dynamodb_client,
                s3_client=self.bsm.s3_client,
            )
            new_data_file_list = list()
            for data_file in data_file_list:
                s3path = S3Path.from_s3_uri(data_file.s3_uri)
                s3path.head_object(bsm=self.bsm.s3_client)
                new_dat_file = {
                    KeyEnum.URI: data_file.s3_uri,
                    KeyEnum.ETAG: data_file.etag,
                    KeyEnum.SIZE: s3path.size,
                    KeyEnum.N_RECORD: data_file.item_count,
                }
                new_data_file_list.append(new_dat_file)

            logger.info(f"Write DbSnapshotManifestSummary to {self.sfn_input.s3path_db_snapshot_manifest_summary.uri}")
            logger.info(f"  preview at: {self.sfn_input.s3path_db_snapshot_manifest_summary.console_url}")
            db_snapshot_manifest_file = DBSnapshotManifestFile.new(
                uri=self.sfn_input.s3path_db_snapshot_manifest_data.uri,
                uri_summary=self.sfn_input.s3path_db_snapshot_manifest_summary.uri,
                data_file_list=new_data_file_list,
                size=None,
                n_record=manifest_summary.item_count,
                calculate=True,
            )
            db_snapshot_manifest_file.write(s3_client=self.bsm.s3_client)

    @classmethod
    def lambda_handler(cls, event: dict, context):  # pragma: no cover
        aws_region = os.environ["AWS_DEFAULT_REGION"]
        bsm = BotoSesManager(region_name=aws_region)
        exec_arn = event["exec_arn"]
        sfn_input = SfnInput(**event["sfn_input"])
        request = cls(
            bsm=bsm,
            exec_arn=exec_arn,
            sfn_input=sfn_input,
        )
        return request.main()


@dataclasses.dataclass
class Step4SnapshotToStagingOrchestrator(Request):
    """
    todo: add docstring
    """

    def main(self):
        """
        :return: db_snapshot_file_group_manifest_file_uri_summary_list, so that
            we can use it to simulate the Map State in local test.
        """
        self.sfn_input.project.s3_client = self.bsm.s3_client
        self.sfn_input.project.step_1_1_plan_snapshot_to_staging()
        Task = (
            self.sfn_input.project.task_model_step_1_2_process_db_snapshot_file_group_manifest_file
        )
        task_list = Task.query_for_unfinished(limit=1000, auto_refresh=True).all()
        db_snapshot_file_group_manifest_file_uri_summary_list = [
            task.data["uri_summary"] for task in task_list
        ]
        payload = [
            # the structure of the payload matches
            # ``Step5ProcessDbSnapshotFileGroupManifest.lambda_handler`` method
            {
                "exec_arn": self.exec_arn,
                "sfn_input": self.sfn_input.to_dict(),
                "uri_summary": uri_summary,
            }
            for uri_summary in db_snapshot_file_group_manifest_file_uri_summary_list
        ]
        self.sfn_input.s3path_snapshot_to_staging_worker_payload.write_text(
            json.dumps(payload, indent=4),
            content_type="application/json",
        )
        # for local development, we return the input parameter for the next step
        return db_snapshot_file_group_manifest_file_uri_summary_list

    @classmethod
    def lambda_handler(cls, event: dict, context):  # pragma: no cover
        """
        .. note::

            It returns ``{"map_payload_bucket": ..., "map_payload_key": ...}``
            for the next Map State to use.
        """
        aws_region = os.environ["AWS_DEFAULT_REGION"]
        bsm = BotoSesManager(region_name=aws_region)
        exec_arn = event["exec_arn"]
        sfn_input = SfnInput(**event["sfn_input"])
        request = cls(
            bsm=bsm,
            exec_arn=exec_arn,
            sfn_input=sfn_input,
        )
        request.main()
        # for lambda function, we return the input parameter for the next
        # lambda function in step function
        return {
            "map_payload_bucket": sfn_input.s3path_snapshot_to_staging_worker_payload.bucket,
            "map_payload_key": sfn_input.s3path_snapshot_to_staging_worker_payload.key,
        }


@dataclasses.dataclass
class Step5ProcessDbSnapshotFileGroupManifest(Request):
    """
    todo: add docstring
    """

    db_snapshot_file_group_manifest_file_uri_summary: str = dataclasses.field()

    @logger.start_and_end(
        msg="Process DB Snapshot File Group Manifest",
    )
    def main(self):
        self.sfn_input.project.s3_client = self.bsm.s3_client

        Task = (
            self.sfn_input.project.task_model_step_1_2_process_db_snapshot_file_group_manifest_file
        )
        task_id = self.db_snapshot_file_group_manifest_file_uri_summary
        task = Task.get_one_or_none(task_id=task_id)
        if not (task.is_pending() or task.is_failed()):
            return

        with Task.start(task_id=task_id, debug=True) as exec_ctx:
            db_snapshot_file_group_manifest_file = DBSnapshotFileGroupManifestFile.read(
                uri_summary=self.db_snapshot_file_group_manifest_file_uri_summary,
                s3_client=self.bsm.s3_client,
            )

            def batch_read_snapshot_data_file_func(
                db_snapshot_file_group_manifest_file,
                **kwargs,
            ):
                return self.sfn_input.batch_read_snapshot_data_file(
                    db_snapshot_file_group_manifest_file=db_snapshot_file_group_manifest_file,
                    s3_client=self.bsm.s3_client,
                )

            basename = db_snapshot_file_group_manifest_file.uri_summary.split("/")[-1]
            new_step_1_3_process_db_snapshot_file_group_manifest_file = (
                logger.start_and_end(
                    msg=f"process manifest file {basename}",
                )(step_1_3_process_db_snapshot_file_group_manifest_file)
            )
            with logger.nested():
                staging_file_group_manifest_file = new_step_1_3_process_db_snapshot_file_group_manifest_file(
                    db_snapshot_file_group_manifest_file=db_snapshot_file_group_manifest_file,
                    s3_client=self.bsm.s3_client,
                    s3_loc=self.sfn_input.s3_loc,
                    batch_read_snapshot_data_file_func=batch_read_snapshot_data_file_func,
                    partition_keys=self.sfn_input.project.partition_keys,
                    sort_by=self.sfn_input.sort_by,
                    descending=self.sfn_input.descending,
                    logger=logger,
                )

    @classmethod
    def lambda_handler(cls, event: dict, context):  # pragma: no cover
        aws_region = os.environ["AWS_DEFAULT_REGION"]
        bsm = BotoSesManager(region_name=aws_region)
        exec_arn = event["exec_arn"]
        sfn_input = SfnInput(**event["sfn_input"])
        uri_summary = event["uri_summary"]
        request = cls(
            bsm=bsm,
            exec_arn=exec_arn,
            sfn_input=sfn_input,
            db_snapshot_file_group_manifest_file_uri_summary=uri_summary,
        )
        return request.main()


@dataclasses.dataclass
class Step6StagingToDatalakeOrchestrator(Request):
    """
    todo: add docstring
    """

    def main(self):
        """
        :return: partition_file_group_manifest_file_uri_summary_list, so that
            we can use it to simulate the Map State in local test.
        """
        self.sfn_input.project.s3_client = self.bsm.s3_client
        self.sfn_input.project.step_2_1_plan_staging_to_datalake()

        Task = (
            self.sfn_input.project.task_model_step_2_2_process_partition_file_group_manifest_file
        )
        task_list = Task.query_for_unfinished(limit=1000, auto_refresh=True).all()
        partition_file_group_manifest_file_uri_summary_list = [
            task.data["uri_summary"] for task in task_list
        ]
        payload = [
            # the structure of the payload matches
            # ``Step7ProcessPartitionFileGroupManifest.lambda_handler`` method
            {
                "exec_arn": self.exec_arn,
                "sfn_input": self.sfn_input.to_dict(),
                "uri_summary": uri_summary,
            }
            for uri_summary in partition_file_group_manifest_file_uri_summary_list
        ]
        self.sfn_input.s3path_staging_to_datalake_worker_payload.write_text(
            json.dumps(payload, indent=4),
            content_type="application/json",
        )

        # for local development, we return the input parameter for the next step
        return partition_file_group_manifest_file_uri_summary_list

    @classmethod
    def lambda_handler(cls, event: dict, context):  # pragma: no cover
        """
        .. note::

            It returns ``{"map_payload_bucket": ..., "map_payload_key": ...}``
            for the next Map State to use.
        """
        aws_region = os.environ["AWS_DEFAULT_REGION"]
        bsm = BotoSesManager(region_name=aws_region)
        exec_arn = event["exec_arn"]
        sfn_input = SfnInput(**event["sfn_input"])
        request = cls(
            bsm=bsm,
            exec_arn=exec_arn,
            sfn_input=sfn_input,
        )
        request.main()
        # for lambda function, we return the input parameter for the next
        # lambda function in step function
        return {
            "map_payload_bucket": sfn_input.s3path_staging_to_datalake_worker_payload.bucket,
            "map_payload_key": sfn_input.s3path_staging_to_datalake_worker_payload.key,
        }


@dataclasses.dataclass
class Step7ProcessPartitionFileGroupManifest(Request):
    """
    todo: add docstring
    """

    partition_file_group_manifest_file_uri_summary: str = dataclasses.field()

    def main(self):
        self.sfn_input.project.s3_client = self.bsm.s3_client
        Task = (
            self.sfn_input.project.task_model_step_2_2_process_partition_file_group_manifest_file
        )
        task_id = self.partition_file_group_manifest_file_uri_summary
        task = Task.get_one_or_none(task_id=task_id)
        if not (task.is_pending() or task.is_failed()):
            return

        with Task.start(task_id=task_id, debug=True) as exec_ctx:
            partition_file_group_manifest_file = PartitionFileGroupManifestFile.read(
                uri_summary=self.partition_file_group_manifest_file_uri_summary,
                s3_client=self.bsm.s3_client,
            )
            basename = partition_file_group_manifest_file.uri_summary.split("/")[-1]
            new_step_2_3_process_partition_file_group_manifest_file = logger.start_and_end(
                msg=f"process manifest file {basename}",
            )(step_2_3_process_partition_file_group_manifest_file)
            with logger.nested():
                staging_file_group_manifest_file = new_step_2_3_process_partition_file_group_manifest_file(
                    partition_file_group_manifest_file=partition_file_group_manifest_file,
                    s3_client=self.bsm.s3_client,
                    s3_loc=self.sfn_input.project.s3_loc,
                    polars_writer=self.sfn_input.project.polars_writer,
                    gzip_compress=self.sfn_input.project.gzip_compression,
                    sort_by=self.sfn_input.sort_by,
                    descending=self.sfn_input.descending,
                    logger=logger,
                )

    @classmethod
    def lambda_handler(cls, event: dict, context):  # pragma: no cover
        aws_region = os.environ["AWS_DEFAULT_REGION"]
        bsm = BotoSesManager(region_name=aws_region)
        exec_arn = event["exec_arn"]
        sfn_input = SfnInput(**event["sfn_input"])
        uri_summary = event["uri_summary"]
        request = cls(
            bsm=bsm,
            exec_arn=exec_arn,
            sfn_input=sfn_input,
            partition_file_group_manifest_file_uri_summary=uri_summary,
        )
        return request.main()


@dataclasses.dataclass
class Step8ValidateResults(Request):
    """
    todo: add docstring
    """

    def main(self) -> dict:
        self.sfn_input.project.s3_client = self.bsm.s3_client
        if self.sfn_input.col_record_count is None:
            print(
                f"You didn't specified `count_on_column` in Step Function input, "
                f"so that the number of record information will not be available in "
                f"validation result."
            )
        result = self.sfn_input.project.step_3_1_validate_datalake()
        result_data = dataclasses.asdict(result)
        s3path = self.sfn_input.s3_loc.s3path_validate_datalake_result
        result_data["result_s3_uri"] = s3path.uri
        result_data["result_s3_console_url"] = s3path.console_url
        return result_data

    @classmethod
    def lambda_handler(cls, event: dict, context):  # pragma: no cover
        aws_region = os.environ["AWS_DEFAULT_REGION"]
        bsm = BotoSesManager(region_name=aws_region)
        exec_arn = event["exec_arn"]
        sfn_input = SfnInput(**event["sfn_input"])
        request = cls(
            bsm=bsm,
            exec_arn=exec_arn,
            sfn_input=sfn_input,
        )
        return request.main()


mapping = {
    RequestTypeEnum.step1_check_and_setup_prerequisites.value: Step1CheckAndSetupPrerequisitesRequest,
    RequestTypeEnum.step2_run_dynamodb_export_job.value: Step2RunDynamoDBExportJob,
    RequestTypeEnum.step3_run_etl_job_planner.value: Step3RunEtlJobPlanner,
    RequestTypeEnum.step4_generate_many_db_snapshot_file_group_manifest_and_dispatch_to_workers.value: Step4SnapshotToStagingOrchestrator,
    RequestTypeEnum.step5_process_db_snapshot_file_group_manifest.value: Step5ProcessDbSnapshotFileGroupManifest,
    RequestTypeEnum.step6_generate_partition_file_group_manifest_and_dispatch_to_workers.value: Step6StagingToDatalakeOrchestrator,
    RequestTypeEnum.step7_process_partition_file_group_manifest.value: Step7ProcessPartitionFileGroupManifest,
    RequestTypeEnum.step8_validate_results.value: Step8ValidateResults,
}
