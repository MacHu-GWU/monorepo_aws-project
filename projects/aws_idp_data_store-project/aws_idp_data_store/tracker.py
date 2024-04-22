# -*- coding: utf-8 -*-

import pynamodb_mate as pm
import aws_textract_pipeline.api as aws_textract_pipeline

from .boto_ses import bsm
from .config.load import config


class StatusAndUpdateTimeIndex(aws_textract_pipeline.BaseStatusAndUpdateTimeIndex):
    pass


class Tracker(aws_textract_pipeline.BaseTracker):
    class Meta:
        table_name = config.env.status_tracking_dynamodb_table_name
        region = bsm.aws_region
        billing_mode = pm.PAY_PER_REQUEST_BILLING_MODE

    status_and_update_time_index = StatusAndUpdateTimeIndex()


with bsm.awscli():
    pm.Connection()
    Tracker.create_table(wait=True)
