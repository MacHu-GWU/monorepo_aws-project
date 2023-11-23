#!/usr/bin/env python
# -*- coding: utf-8 -*-

# helpers
from automation.logger import logger
from automation.emoji import Emoji

# actions
from automation.venv import create_virtualenv
from automation.deps import (
    poetry_export,
    pip_install,
    pip_install_dev,
    pip_install_test,
    pip_install_automation,
)


@logger.start_and_end(
    msg="Install Phase",
    start_emoji=f"{Emoji.start} {Emoji.pre_build_phase}",
    end_emoji=Emoji.install_phase,
    pipe=Emoji.install_phase,
)
def install_phase():
    with logger.nested():
        create_virtualenv()
        poetry_export()
        pip_install_automation()
        pip_install()
        pip_install_dev()
        pip_install_test()


install_phase()
