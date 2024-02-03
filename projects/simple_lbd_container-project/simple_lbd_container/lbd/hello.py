# -*- coding: utf-8 -*-

"""
This lambda function takes a name as input and echo back ``hello {name}``

Sample input::

    {"name": "Alice}

Sample output::

    {"message": "hello Alice"}
"""

from ..logger import logger


@logger.pretty_log()
def low_level_api(name: str) -> dict:
    message = f"hello {name}"
    logger.info(message)
    return {"message": message}


def lambda_handler(event: dict, context):  # pragma: no cover
    return low_level_api(event.get("name", "Mr X"))
