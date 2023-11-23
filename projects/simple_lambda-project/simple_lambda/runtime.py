# -*- coding: utf-8 -*-

"""
**"Runtime" Definition**

Runtime is where you execute your code. For example, if this code is running
in a CI build environment, then the runtime is "ci". If this code is running
on your local laptop, then the runtime is "local". If this code is running on
AWS Lambda, then the runtime is "lambda"

This module automatically detect what is the current runtime.

.. note::

    This module is "ZERO-DEPENDENCY".
"""

import os
import enum

IS_LAMBDA = False
IS_CI = False
IS_LOCAL = False


class RunTimeEnum(str, enum.Enum):
    local = "loc"
    ci = "ci"
    awslambda = "lambda"
    unknown = "unknown"


CURRENT_RUNTIME: str = RunTimeEnum.unknown.value

if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:  # pragma: no cover
    IS_LAMBDA = True
    CURRENT_RUNTIME = RunTimeEnum.awslambda.value
# if you use AWS CodeBuild for CI/CD
# ref: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html
elif "CODEBUILD_CI" in os.environ:  # pragma: no cover
    IS_CI = True
    CURRENT_RUNTIME = RunTimeEnum.ci.value
# if you use GitHub CI for CI/CD
# ref: https://docs.github.com/en/actions/learn-github-actions/variables
# if you use Circle CI for CI/CD
# ref: https://circleci.com/docs/variables/
else:  # pragma: no cover
    IS_LOCAL = True
    CURRENT_RUNTIME = RunTimeEnum.local.value
