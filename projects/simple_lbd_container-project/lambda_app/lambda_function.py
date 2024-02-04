# -*- coding: utf-8 -*-

from simple_lbd_container.lbd.hello import lambda_handler as hello_handler
from simple_lbd_container.lbd.s3sync import lambda_handler as s3sync_handler


handler_mapper = dict(
    hello_handler=hello_handler,
    s3sync_handler=s3sync_handler,
)


def handler(event, context):
    func = handler_mapper[event["handler"]]
    response = func(event=event["event"], context=context)
    return response
