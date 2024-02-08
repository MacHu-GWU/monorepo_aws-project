# -*- coding: utf-8 -*-

import os
import dataclasses

import pytest
from pathlib_mate import Path

from simple_glue.boto_ses import bsm
from simple_glue.config.api import config
from simple_glue.glue_jobs.unnest import Param


def test_glue_etl():
    # before invoke
    s3dir_input = config.env.s3dir_env_data.joinpath("unittest/unnest/input").to_dir()
    s3dir_output = config.env.s3dir_env_data.joinpath("unittest/unnest/output").to_dir()
    param = Param(
        s3uri_input=s3dir_input.uri,
        s3uri_output=s3dir_output.uri,
    )
    dir_unnest = Path.dir_here(__file__).parent.joinpath(
        "tests_glue_int", "data", "unnest"
    )
    s3dir_input.upload_dir(dir_unnest, overwrite=True)
    s3dir_output.delete()

    # invoke
    bsm.glue_client.start_job_run(
        JobName=config.env.glue_unnest.name,
        Arguments={f"--{k}": v for k, v in dataclasses.asdict(param).items()},
    )


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
