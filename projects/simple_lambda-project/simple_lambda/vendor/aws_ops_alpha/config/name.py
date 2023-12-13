# -*- coding: utf-8 -*-

"""
Naming convention related configs.
"""

import typing as T
import dataclasses

if T.TYPE_CHECKING:  # pragma: no cover
    from .main import BaseEnv


@dataclasses.dataclass
class NameMixin:
    """
    This mixin class derive all AWS Resource name based on the project name
    and the env name.
    """

    @property
    def cloudformation_stack_name(self: "BaseEnv") -> str:
        """
        Cloudformation stack name.
        """
        return self.prefix_name_slug
