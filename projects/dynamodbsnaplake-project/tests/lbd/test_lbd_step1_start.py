# -*- coding: utf-8 -*-

import moto
import uuid

from dynamodbsnaplake.logger import logger
from dynamodbsnaplake.config.api import config
from dynamodbsnaplake.lbd.common import ExecutionContext
from dynamodbsnaplake.lbd import step1_start
from dynamodbsnaplake.lbd import step2_run_job
from dynamodbsnaplake.lbd import step3_check_status
from dynamodbsnaplake.tests.mock_aws import BaseMockAws


class Test(BaseMockAws):
    mock_list = [
        moto.mock_s3,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bsm.s3_client.create_bucket(Bucket=config.env.s3dir_sfn_executions.bucket)

    def _test(self):
        execution_id = uuid.uuid4().hex
        step1_start.low_level_api(
            s3_client=self.bsm.s3_client,
            bucket=config.env.s3dir_sfn_executions.bucket,
            prefix=config.env.s3dir_sfn_executions.key,
            execution_id=execution_id,
            dry_run=True,
        )
        exec_context = ExecutionContext.read(
            s3_client=self.bsm.s3_client,
            bucket=config.env.s3dir_sfn_executions.bucket,
            prefix=config.env.s3dir_sfn_executions.key,
            exec_id=execution_id,
        )

        step2_run_job.low_level_api(
            s3_client=self.bsm.s3_client,
            bucket=config.env.s3dir_sfn_executions.bucket,
            prefix=config.env.s3dir_sfn_executions.key,
            execution_id=execution_id,
            instant_finish=True,
            always_succeed=True,
        )
        exec_context = ExecutionContext.read(
            s3_client=self.bsm.s3_client,
            bucket=config.env.s3dir_sfn_executions.bucket,
            prefix=config.env.s3dir_sfn_executions.key,
            exec_id=execution_id,
        )

        res = step3_check_status.low_level_api(
            s3_client=self.bsm.s3_client,
            bucket=config.env.s3dir_sfn_executions.bucket,
            prefix=config.env.s3dir_sfn_executions.key,
            execution_id=execution_id,
        )
        assert res["status"] == "succeeded"

    def test(self):
        with logger.disabled(
            disable=True,  # mute log
            # disable=False,  # show log
        ):
            self._test()


if __name__ == "__main__":
    from dynamodbsnaplake.tests import run_cov_test

    run_cov_test(__file__, "dynamodbsnaplake.lbd.step1_start", preview=False)
