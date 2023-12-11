# -*- coding: utf-8 -*-

import enum


class StepEnum(str, enum.Enum):
    CREATE_VIRTUALENV = "CREATE_VIRTUALENV"
    INSTALL_DEPENDENCIES = "INSTALL_DEPENDENCIES"
    BUILD_SOURCE_CODE = "BUILD_SOURCE_CODE"
    RUN_CODE_COVERAGE_TEST = "RUN_CODE_COVERAGE_TEST"
    PUBLISH_DOCUMENTATION_WEBSITE = "PUBLISH_DOCUMENTATION_WEBSITE"
    PUBLISH_PYPI_VERSION = "PUBLISH_PYPI_VERSION"


class GitBranchNameEnum(str, enum.Enum):
    main = "main"
    feature = "feature"
    fix = "fix"
    test = "test"
    doc = "doc"
    release = "release"


class EnvNameEnum(str, enum.Enum):
    devops = "devops"
    sbx = "sbx"


class RuntimeNameEnum(str, enum.Enum):
    local = "local"
    ci = "ci"

