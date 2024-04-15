# -*- coding: utf-8 -*-

import json
import aws_cdk as cdk
import aws_cdk.assertions as assertions
from aws_idp_data_store.iac.define import MainStack
from aws_idp_data_store.config.api import config


def test():
    app = cdk.App()
    stack = MainStack(
        app,
        config.env.env_name,
        config=config,
        env=config.env,
        stack_name=config.env.prefix_name_slug,
    )
    for key, value in config.env.workload_aws_tags.items():
        cdk.Tags.of(app).add(key, value)
    template = assertions.Template.from_stack(stack)
    # print(json.dumps(template.to_json(), indent=4))


if __name__ == "__main__":
    from aws_idp_data_store.tests import run_cov_test

    run_cov_test(__file__, "aws_idp_data_store.iac.define", preview=False)
