# -*- coding: utf-8 -*-

import enum


class StepEnum(str, enum.Enum):
    CREATE_VIRTUALENV = "CREATE_VIRTUALENV"
    INSTALL_DEPENDENCIES = "INSTALL_DEPENDENCIES"
    BUILD_LAMBDA_SOURCE_LOCALLY = "BUILD_LAMBDA_SOURCE_LOCALLY"
    RUN_CODE_COVERAGE_TEST = "RUN_CODE_COVERAGE_TEST"
    PUBLISH_DOCUMENTATION_WEBSITE = "PUBLISH_DOCUMENTATION_WEBSITE"
    PUBLISH_LAMBDA_LAYER = "PUBLISH_LAMBDA_LAYER"
    DEPLOY_LAMBDA_APP_VIA_CDK = "DEPLOY_LAMBDA_APP_VIA_CDK"
    RUN_INTEGRATION_TEST = "RUN_INTEGRATION_TEST"
    PUBLISH_NEW_LAMBDA_VERSION = "PUBLISH_NEW_LAMBDA_VERSION"
    CREATE_CONFIG_SNAPSHOT = "CREATE_CONFIG_SNAPSHOT"
    CREATE_GIT_TAG = "CREATE_GIT_TAG"
    DELETE_LAMBDA_APP_IN_SBX = "DELETE_LAMBDA_APP_IN_SBX"
    DELETE_LAMBDA_APP_IN_TST = "DELETE_LAMBDA_APP_IN_TST"
    DELETE_LAMBDA_APP_IN_STG = "DELETE_LAMBDA_APP_IN_STG"
    DELETE_LAMBDA_APP_IN_PRD = "DELETE_LAMBDA_APP_IN_PRD"


class GitBranchNameEnum(str, enum.Enum):
    main = "main"
    feature = "feature"
    fix = "fix"
    doc = "doc"
    layer = "layer"
    app = "app"
    release = "release"
    cleanup = "cleanup"


class EnvNameEnum(str, enum.Enum):
    devops = "devops"
    sbx = "sbx"
    tst = "tst"
    stg = "stg"
    prd = "prd"


class RuntimeNameEnum(str, enum.Enum):
    local = "local"
    ci = "ci"

