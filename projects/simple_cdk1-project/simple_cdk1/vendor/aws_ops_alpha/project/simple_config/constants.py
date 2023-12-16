# -*- coding: utf-8 -*-

from ...vendor.better_enum import BetterStrEnum


class StepEnum(BetterStrEnum):
    DEPLOY_CONFIG = "DEPLOY_CONFIG"
    CREATE_CONFIG_SNAPSHOT = "CREATE_CONFIG_SNAPSHOT"
    DELETE_CONFIG = "DELETE_CONFIG"


class GitBranchNameEnum(BetterStrEnum):
    main = "main"
    release = "release"


class EnvNameEnum(BetterStrEnum):
    devops = "devops"


class RuntimeNameEnum(BetterStrEnum):
    local = "local"
    ci = "ci"
