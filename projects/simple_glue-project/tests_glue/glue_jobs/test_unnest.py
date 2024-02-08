# -*- coding: utf-8 -*-

import sys

import pytest

from pyspark.context import SparkContext
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

from awsglue.dynamicframe import DynamicFrame
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


from simple_glue.glue_jobs.unnest import transform_data


@pytest.fixture(scope="module", autouse=True)
def glue_context():
    sys.argv.append("--JOB_NAME")
    sys.argv.append("test")

    args = getResolvedOptions(sys.argv, ["JOB_NAME"])

    glue_ctx = GlueContext(SparkContext.getOrCreate())

    job = Job(glue_ctx)
    job.init(args["JOB_NAME"], args)

    yield (glue_ctx)

    job.commit()


def test_transform_data(glue_context):
    # pre-installed python package in glue runtime goes here
    import pandas as pd  # this import is not used, it is just an example

    # prepare input data
    pdf = glue_context.createDataFrame(
        [
            ("e-1", {"name": "measurement", "value": 1}),
            ("e-2", {"name": "measurement", "value": 2}),
            ("e-3", {"name": "measurement", "value": 3}),
        ],
        schema=StructType(
            [
                StructField("event_id", StringType()),
                StructField(
                    "details",
                    StructType(
                        [
                            StructField("name", StringType()),
                            StructField("value", IntegerType()),
                        ]
                    ),
                ),
            ]
        ),
    )
    gdf = DynamicFrame.fromDF(
        pdf,
        glue_context,
        name="gdf",
    )

    # run ``transform_data()``
    gdf_transformed = transform_data(gdf)

    # example the output
    pdf_transformed = gdf_transformed.toDF()
    records = pdf_transformed.toPandas().to_dict(orient="records")
    assert records == [
        {"event_id": "e-1", "details.name": "measurement", "details.value": 2},
        {"event_id": "e-2", "details.name": "measurement", "details.value": 4},
        {"event_id": "e-3", "details.name": "measurement", "details.value": 6},
    ]
    print("")
    pdf_transformed.show()


if __name__ == "__main__":
    from simple_glue.tests.glue import run_unit_test

    run_unit_test(__file__, glue_version="4.0")
