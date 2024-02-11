# -*- coding: utf-8 -*-

"""
This module implements the automation to manage AWS lambda artifacts, versions, etc ...
"""

import typing as T
import subprocess
from pathlib import Path

import aws_console_url.api as aws_console_url
from ..vendor.emoji import Emoji
from ..vendor.hashes import hashes

from ..logger import logger


if T.TYPE_CHECKING:  # pragma: no cover
    import pyproject_ops.api as pyops
    from boto_session_manager import BotoSesManager
    from s3pathlib import S3Path
