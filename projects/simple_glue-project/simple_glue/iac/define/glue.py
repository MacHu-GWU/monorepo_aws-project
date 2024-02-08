# -*- coding: utf-8 -*-

import typing as T

import aws_cdk as cdk
from aws_cdk import (
    aws_glue as glue,
)

from ...boto_ses import boto_ses_factory

if T.TYPE_CHECKING:
    from .main import MainStack


class GlueMixin:
    def mk_rg2_glue(self: "MainStack"):
        self.glue_job_mapper: T.Dict[str : T.Dict[str, glue.CfnJob]] = dict()
        for glue_job in self.env.glue_jobs.values():
            cfn_glue_job = glue.CfnJob(
                self,
                id=f"GlueJob{glue_job.short_name_camel}",
                name=glue_job.name,
                command=glue.CfnJob.JobCommandProperty(
                    name="glueetl",
                    script_location=glue_job.get_s3path_mutable_etl_script_py(
                        bsm_devops=boto_ses_factory.bsm_devops,
                    ).uri,
                ),
                role=self.iam_role_for_glue.role_arn,
                glue_version=glue_job.glue_version,
                worker_type=glue_job.worker_type,
                number_of_workers=glue_job.number_of_workers,
                execution_property=glue.CfnJob.ExecutionPropertyProperty(
                    max_concurrent_runs=glue_job.max_concurrent_runs,
                ),
                max_retries=glue_job.max_retries,
                timeout=glue_job.timeout,
                default_arguments={
                    # please reference the requirements.txt file
                    "--additional-python-modules": ",".join(
                        [
                            "func-args==0.1.1",
                            "iterproxy==0.3.1",
                            "pathlib-mate==1.3.2",
                            "boto-session-manager==1.7.2",
                            "smart-open==6.2.0",
                            "s3pathlib==2.1.2",
                        ]
                    ),
                    "--extra-py-files": glue_job.get_s3path_glue_extra_py_files_zip(
                        bsm_devops=boto_ses_factory.bsm_devops,
                    ).uri,
                },
            )
            self.glue_job_mapper[glue_job.name] = cfn_glue_job
            cdk.Tags.of(cfn_glue_job).add(
                "tech:glue_python_lib_version",
                glue_job.target_lib_live_version,
            )
            cdk.Tags.of(cfn_glue_job).add(
                "tech:glue_etl_script_version",
                glue_job.target_script_live_version,
            )
