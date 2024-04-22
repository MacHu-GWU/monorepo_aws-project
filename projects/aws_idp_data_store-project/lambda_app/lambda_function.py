# -*- coding: utf-8 -*-

from aws_idp_data_store.lbd.hello import lambda_handler as hello_handler
from aws_idp_data_store.lbd.s3sync import lambda_handler as s3sync_handler
from aws_idp_data_store.lbd.textract import lambda_handler as landing_to_raw_handler
from aws_idp_data_store.lbd.textract import lambda_handler as raw_to_tt_handler
from aws_idp_data_store.lbd.textract import lambda_handler as tt_to_text_handler
