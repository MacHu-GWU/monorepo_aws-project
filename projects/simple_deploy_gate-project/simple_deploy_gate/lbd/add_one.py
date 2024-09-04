# -*- coding: utf-8 -*-

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from pynamodb.models import PAY_PER_REQUEST_BILLING_MODE
from pynamodb.exceptions import UpdateError

from ..config.api import config
from ..boto_ses import bsm


# Define Dynamodb Table and Schema
class Counter(Model):
    class Meta:
        table_name = config.env.dynamodb_table_name
        region = bsm.aws_region
        billing_mode = PAY_PER_REQUEST_BILLING_MODE

    key = UnicodeAttribute(hash_key=True)
    count = NumberAttribute(default=0)


def low_level_api(key: str):
    """
    If a key not exists, create it and set count to 1. If exists, count + 1
    """
    item = Counter(key=key)
    try:
        item.update(actions=[Counter.count.set(Counter.count + 1)])
    except UpdateError:
        item.count = 1
        item.save()
    except Exception as e:  # pragma: no cover
        return {"message": "error: {}".format(e)}
    return {"message": "success"}


def handler(event, context):  # pragma: no cover
    return low_level_api(event["key"])
