# -*- coding: utf-8 -*-

import typing as T
import dataclasses

if T.TYPE_CHECKING: # pragma: no cover
    from .main import Env


@dataclasses.dataclass
class NameMixin:
    """
    This mixin class derive all AWS Resource name based on the project name
    and the env name.
    """
    @property
    def cloudformation_stack_name(self: "Env") -> str:
        return self.prefix_name_slug
