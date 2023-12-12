# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager

bsm = BotoSesManager(
    profile_name="bmt_app_dev_us_east_1",
    region_name="us-east-1",
)
