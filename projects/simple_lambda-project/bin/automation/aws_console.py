# -*- coding: utf-8 -*-

import typing as T
from aws_console_url import AWSConsole

if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager


def get_aws_console(bsm: "BotoSesManager") -> AWSConsole:
    return AWSConsole(
        aws_account_id=bsm.aws_account_id,
        aws_region=bsm.aws_region,
        bsm=bsm,
    )
