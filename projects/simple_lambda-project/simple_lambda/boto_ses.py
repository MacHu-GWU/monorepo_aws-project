# -*- coding: utf-8 -*-

from s3pathlib import context
from boto_session_manager import BotoSesManager

from .runtime import IS_LOCAL, IS_CI, IS_LAMBDA

# environment aware boto session manager
if IS_LAMBDA:  # put production first
    bsm = BotoSesManager(
        region_name="us-east-1",
    )
elif IS_LOCAL:
    bsm = BotoSesManager(
        profile_name="bmt_app_dev_us_east_1",
        region_name="us-east-1",
    )
elif IS_CI:
    bsm = BotoSesManager(
        region_name="us-east-1",
    )
else:  # pragma: no cover
    raise NotImplementedError

# Set default s3pathlib boto session
context.attach_boto_session(boto_ses=bsm.boto_ses)
