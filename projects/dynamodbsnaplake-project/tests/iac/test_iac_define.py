# -*- coding: utf-8 -*-

import json
import aws_cdk as cdk
import aws_cdk.assertions as assertions
from dynamodbsnaplake.iac.define import MainStack
from dynamodbsnaplake.config.api import config
from dynamodbsnaplake.paths import dir_project_root


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
    cfn_content = json.dumps(template.to_json(), indent=4)
    # print(cfn_content)
    # dir_project_root.joinpath("cfn.json").write_text(cfn_content)


if __name__ == "__main__":
    from dynamodbsnaplake.tests import run_cov_test

    run_cov_test(__file__, "dynamodbsnaplake.iac.define", preview=False)
