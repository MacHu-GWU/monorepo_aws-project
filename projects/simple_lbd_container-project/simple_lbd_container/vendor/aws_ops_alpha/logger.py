# -*- coding: utf-8 -*-

from .vendor.nested_logger import NestedLogger

logger = NestedLogger(
    name="aws_ops_alpha",
    log_format="%(message)s",
)

# rich console is optional
try:
    from rich.console import Console

    console = Console()
except ImportError:  # pragma: no cover
    # todo: tell user to install rich when user attempt to use console variable
    pass
