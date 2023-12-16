# -*- coding: utf-8 -*-

from ...rule.rule_set import RuleSet
from ...paths import dir_python_lib

rule_set = RuleSet.from_folder(
    path_folder=dir_python_lib.joinpath("project", "simple_python"),
)
