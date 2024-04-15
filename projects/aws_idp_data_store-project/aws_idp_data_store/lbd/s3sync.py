# -*- coding: utf-8 -*-

"""
This lambda function is triggered by S3 put event and copy the file from source
to target bucket. The target bucket is defined in the configuration.
"""

from s3pathlib import S3Path
from aws_lambda_event import S3PutEvent

from ..config.load import config
from ..logger import logger


def low_level_api(
    s3path_source: S3Path,
):
    logger.info(f"copy {s3path_source.uri}")
    logger.info(f"preview: {s3path_source.console_url}", indent=1)

    s3path_target = config.env.s3dir_target.joinpath(
        s3path_source.relative_to(config.env.s3dir_source)
    )
    logger.info(f"to {s3path_target.uri}")
    logger.info(f"preview: {s3path_target.console_url}", indent=1)
    s3path_source.copy_to(s3path_target, overwrite=True)


def lambda_handler(event: dict, context: str):  # pragma: no cover
    s3put_event = S3PutEvent(**event)
    return low_level_api(
        s3path_source=S3Path(
            s3put_event.Records[0].bucket,
            s3put_event.Records[0].key,
        ),
    )
