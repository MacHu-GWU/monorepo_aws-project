# -*- coding: utf-8 -*-

import dataclasses


@dataclasses.dataclass
class BaseModel:
    @classmethod
    def from_dict(cls, dct: dict):
        return cls(**dct)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
