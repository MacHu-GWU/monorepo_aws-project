# -*- coding: utf-8 -*-

from .vendor.nested_logger import NestedLogger
from .paths import PACKAGE_NAME

logger = NestedLogger(
    name=PACKAGE_NAME,
    log_format="%(message)s",
)
