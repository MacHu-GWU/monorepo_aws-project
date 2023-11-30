# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
from aws_cloudformation.api import remove_stack

from ..config_init import config


def main():
    bsm = BotoSesManager(
        profile_name=config.github_action_open_id_connection.aws_profile
    )
    remove_stack(
        bsm=bsm,
        stack_name=config.github_action_open_id_connection.stack_name,
        skip_prompt=False,
    )
