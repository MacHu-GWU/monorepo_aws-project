# -*- coding: utf-8 -*-

import aws_cdk as cdk
from simple_deploy_gate.iac.define import MainStack
from simple_deploy_gate.config.api import config

app = cdk.App()

stack = MainStack(
    app,
    config.env.env_name,
    config=config,
    env=config.env,
    stack_name=config.env.cloudformation_stack_name,
)

app.synth()
