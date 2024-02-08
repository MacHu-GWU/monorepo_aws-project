# -*- coding: utf-8 -*-

import sys

import pytest

from pyspark.context import SparkContext

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

from pathlib_mate import Path
from s3pathlib import S3Path
from simple_glue.boto_ses import bsm
from simple_glue.config.api import config
from simple_glue.glue_jobs.unnest import GlueETL


@pytest.fixture(scope="module", autouse=True)
def glue_context():
    sys.argv.append("--JOB_NAME")
    sys.argv.append("test_count")

    args = getResolvedOptions(sys.argv, ["JOB_NAME"])

    glue_ctx = GlueContext(SparkContext.getOrCreate())

    job = Job(glue_ctx)
    job.init(args["JOB_NAME"], args)

    yield (glue_ctx)

    job.commit()


def setup_module(module):
    s3dir_input = config.env.s3dir_env_data.joinpath("unittest/unnest/input").to_dir()
    s3dir_output = config.env.s3dir_env_data.joinpath("unittest/unnest/output").to_dir()
    dir_unnest = Path.dir_here(__file__).joinpath("data", "unnest")
    s3dir_input.upload_dir(dir_unnest, overwrite=True)
    s3dir_output.delete()


def test_glue_etl(glue_context):
    gdf_transformed = GlueETL().run()
    assert gdf_transformed.count() == 12
    print("")
    gdf_transformed.toDF().show()


if __name__ == "__main__":
    from simple_glue.tests.glue import run_unit_test

    run_unit_test(__file__, glue_version="4.0")
