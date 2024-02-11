# -*- coding: utf-8 -*-

"""
Step Function deployment related configurations.
"""

import typing as T
import dataclasses

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import Env


@dataclasses.dataclass
class StepFunctionDeployMixin:
    """
    Step Function deployment related configurations.
    """
