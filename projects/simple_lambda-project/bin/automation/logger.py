# -*- coding: utf-8 -*-

from rich.console import Console

from .vendor.nested_logger import NestedLogger

logger = NestedLogger(
    name="automation",
    log_format="%(message)s",
)

console = Console()
