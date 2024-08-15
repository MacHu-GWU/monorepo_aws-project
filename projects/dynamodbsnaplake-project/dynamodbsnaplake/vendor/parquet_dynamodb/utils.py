# -*- coding: utf-8 -*-


import base64
from datetime import datetime, timezone


def b64encode_string(s: str) -> str:
    return base64.urlsafe_b64encode(s.encode("utf-8")).decode("utf-8")


def b64decode_string(s: str) -> str:
    return base64.urlsafe_b64decode(s.encode("utf-8")).decode("utf-8")


def dt_to_str(datetime: datetime) -> str:
    """
    Convert a datetime object to a formatted string.
    """
    return datetime.astimezone(timezone.utc).strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]


def str_to_dt(s: str) -> datetime:
    """
    Convert a formatted string to a datetime object.
    """
    return datetime.strptime(s, "%Y_%m_%d_%H_%M_%S_%f").replace(tzinfo=timezone.utc)
