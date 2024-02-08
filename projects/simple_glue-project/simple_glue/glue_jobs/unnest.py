# -*- coding: utf-8 -*-

"""
This is a sample Glue Job to demonstrate:

- Glue job scripting best practice
    - Parameter management
    - Fast development in interactive Glue Jupyter Notebook
- Glue job unit test best practice
- Glue job integration test best practice
"""

# standard library
import typing as T
import sys
import os
import dataclasses
from pprint import pprint

# third party library
from s3pathlib import S3Path

# pyspark and glue stuff
from pyspark.context import SparkContext

from awsglue.dynamicframe import DynamicFrame
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# custom library
from simple_glue.glue_libs.glue_utils import double_a_column
# identify the current run Mode
IS_GLUE_JOB_RUN = False
IS_DEV_NOTEBOOK = False
IS_LOCAL = False

# in real glue job runtime, it always has --JOB_RUN_ID argument
if "--JOB_RUN_ID" in sys.argv:
    IS_GLUE_JOB_RUN = True
    print("Now we are on GLUE_JOB_RUN mode")
# in Jupyter Notebook glue job runtime, the $HOME is /home/spark
elif os.environ["HOME"] == "/home/spark":
    IS_DEV_NOTEBOOK = True
    print("Now we are on DEV_NOTEBOOK mode")
# otherwise, we assume that we are on local development or CI runtime for development or testing
else:
    IS_LOCAL = True
    print("Now we are on IS_LOCAL mode")

# Sometimes you can force to run in DEV_NOTEBOOK mode in regular Glue job run for debugging
# Also you can force to run in GLUE_JOB_RUN mode in your jupyter notebook, for example, testing the production data connection
# ensure that you commented this out before committing the code

# IS_GLUE_JOB_RUN = True
# IS_DEV_NOTEBOOK = True
@dataclasses.dataclass
class Param:
    s3uri_input: str
    s3uri_output: str

    @classmethod
    def load(cls, args: T.Optional[T.Dict[str, str]]):
        if IS_GLUE_JOB_RUN:
            return cls(
                s3uri_input=args.get("s3uri_input"),
                s3uri_output=args.get("s3uri_output"),
            )
        else:
            return cls(
                s3uri_input="s3://807388292768-us-east-1-data/projects/simple_glue/dev/unittest/unnest/input/",
                s3uri_output="s3://807388292768-us-east-1-data/projects/simple_glue/dev/unittest/unnest/output/",
            )

    @property
    def s3dir_input(self) -> S3Path:
        """
        The S3Path object version of the input S3 folder.
        """
        return S3Path(self.s3uri_input)

    @property
    def s3dir_output(self) -> S3Path:
        """
        The S3Path object version of the output S3 folder.
        """
        return S3Path(self.s3uri_output)
def transform_data(gdf: DynamicFrame) -> DynamicFrame:
    """
    unnest / flatten complicte object and double the value of the columhn ``details.value``.
    """
    gdf_transformed = gdf.unnest(transformation_ctx="gdf_unnested")
    gdf_transformed = double_a_column(
        gdf_transformed,
        col_name="details.value",
        trans_ctx="double_a_column"
    )
    return gdf_transformed
class GlueETL:
    def run(self):
        self.step0_preprocess()
        self.step1_read_data()
        self.step2_transform_data()
        self.step3_write_data()
        self.step4_post_process()
        return self.gdf_transformed

    def step0_preprocess(self):
        # print("--- sys.argv ---")
        # pprint(sys.argv)
        # print("--- env vars ---")
        # for k, v in os.environ.items():
        #     print(f"{k}={v}")

        self.spark_ctx = SparkContext.getOrCreate()
        self.glue_ctx = GlueContext(self.spark_ctx)
        self.spark_ses = self.glue_ctx.spark_session

        if IS_GLUE_JOB_RUN:
            self.args = getResolvedOptions(
                sys.argv,
                [
                    "JOB_NAME",
                    "s3uri_input",
                    "s3uri_output",
                ]
            )
            self.job = Job(self.glue_ctx)
            self.job.init(self.args["JOB_NAME"], self.args)
        else:
            self.args = None
            self.job = None

        self.param = Param.load(self.args)

    def step1_read_data(self):
        self.gdf = self.glue_ctx.create_dynamic_frame.from_options(
            connection_type="s3",
            connection_options=dict(
                paths=[
                    self.param.s3dir_input.uri,
                ],
                recurse=True,
            ),
            format="json",
            format_options=dict(multiLine="true"),
            transformation_ctx="read_gdf",
        )

    def step2_transform_data(self):
        self.gdf_transformed = transform_data(self.gdf)

    def step3_write_data(self):
        self.glue_ctx.write_dynamic_frame.from_options(
            frame=self.gdf_transformed,
            connection_type="s3",
            connection_options=dict(
                path=self.param.s3dir_output.uri,
            ),
            format="parquet",
            transformation_ctx="write_gdf",
        )

    def step4_post_process(self):
        # only commit job in real Glue job run
        if IS_GLUE_JOB_RUN:
            self.job.commit()
# If it is not LOCAL runtime, we should run the ETL logics
if IS_LOCAL is False:
    gdf_transformed = GlueETL().run()
    if IS_DEV_NOTEBOOK:
        gdf_transformed.toDF().show()
