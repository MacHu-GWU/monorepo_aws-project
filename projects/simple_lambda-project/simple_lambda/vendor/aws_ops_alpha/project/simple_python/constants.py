# -*- coding: utf-8 -*-

from ...vendor.better_enum import BetterStrEnum


class StepEnum(BetterStrEnum):
    CREATE_VIRTUALENV = "CREATE_VIRTUALENV"
    INSTALL_DEPENDENCIES = "INSTALL_DEPENDENCIES"
    BUILD_SOURCE_CODE = "BUILD_SOURCE_CODE"
    RUN_CODE_COVERAGE_TEST = "RUN_CODE_COVERAGE_TEST"
    PUBLISH_DOCUMENTATION_WEBSITE = "PUBLISH_DOCUMENTATION_WEBSITE"
    PUBLISH_PYPI_VERSION = "PUBLISH_PYPI_VERSION"


class GitBranchNameEnum(BetterStrEnum):
    main = "main"
    feature = "feature"
    fix = "fix"
    test = "test"
    doc = "doc"
    release = "release"


class EnvNameEnum(BetterStrEnum):
    devops = "devops"
    sbx = "sbx"


class RuntimeNameEnum(BetterStrEnum):
    local = "local"
    ci = "ci"

