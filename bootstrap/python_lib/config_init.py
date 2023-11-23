# -*- coding: utf-8 -*-

from .config_def import Config
from .paths import path_config

config = Config.load(path_config)
