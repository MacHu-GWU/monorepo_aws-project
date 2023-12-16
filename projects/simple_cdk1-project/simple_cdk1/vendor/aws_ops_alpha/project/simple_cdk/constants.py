# -*- coding: utf-8 -*-

from ...vendor.better_enum import BetterStrEnum


class StepEnum(BetterStrEnum):
    CREATE_VIRTUALENV = "CREATE_VIRTUALENV"
    INSTALL_DEPENDENCIES = "INSTALL_DEPENDENCIES"
    DEPLOY_CONFIG = "DEPLOY_CONFIG"
    RUN_CODE_COVERAGE_TEST = "RUN_CODE_COVERAGE_TEST"
    PUBLISH_DOCUMENTATION_WEBSITE = "PUBLISH_DOCUMENTATION_WEBSITE"
    DEPLOY_CDK_STACK = "DEPLOY_CDK_STACK"
    RUN_INTEGRATION_TEST = "RUN_INTEGRATION_TEST"
    CREATE_CONFIG_SNAPSHOT = "CREATE_CONFIG_SNAPSHOT"
    CREATE_GIT_TAG = "CREATE_GIT_TAG"
    DELETE_CDK_STACK_IN_SBX = "DELETE_CDK_STACK_IN_SBX"
    DELETE_CDK_STACK_IN_TST = "DELETE_CDK_STACK_IN_TST"
    DELETE_CDK_STACK_IN_STG = "DELETE_CDK_STACK_IN_STG"
    DELETE_CDK_STACK_IN_PRD = "DELETE_CDK_STACK_IN_PRD"
    DELETE_CONFIG = "DELETE_CONFIG"


class GitBranchNameEnum(BetterStrEnum):
    main = "main"
    feature = "feature"
    fix = "fix"
    doc = "doc"
    app = "app"
    release = "release"
    cleanup = "cleanup"


class EnvNameEnum(BetterStrEnum):
    devops = "devops"
    sbx = "sbx"
    tst = "tst"
    stg = "stg"
    prd = "prd"


class RuntimeNameEnum(BetterStrEnum):
    local = "local"
    ci = "ci"
