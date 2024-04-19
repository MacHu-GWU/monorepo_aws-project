# -*- coding: utf-8 -*-

import typing as T
import json
import gzip


def json_dump_to_gz_data(data: T.Union[dict, list], **kwargs) -> bytes:
    return gzip.compress(json.dumps(data, **kwargs).encode("utf-8"))


def json_load_from_gz_data(b: bytes) -> T.Union[dict, list]:
    return json.loads(gzip.decompress(b).decode("utf-8"))
