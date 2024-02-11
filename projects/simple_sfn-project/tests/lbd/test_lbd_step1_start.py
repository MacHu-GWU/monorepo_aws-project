# -*- coding: utf-8 -*-

import moto
import uuid

from simple_sfn.logger import logger
from simple_sfn.config.api import config
from simple_sfn.lbd.common import ExecutionContext
from simple_sfn.lbd import step1_start
from simple_sfn.lbd import step2_run_job
from simple_sfn.lbd import step3_check_status
from simple_sfn.tests.mock_aws import BaseMockAws


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
    from simple_sfn.tests import run_cov_test

    run_cov_test(__file__, "simple_sfn.lbd.step1_start", preview=False)
