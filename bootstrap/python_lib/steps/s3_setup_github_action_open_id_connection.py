# -*- coding: utf-8 -*-

from ..config_init import config
from ..setup_github_action_open_id_connection import (
    setup_github_action_open_id_connection,
)


def main():
    setup_github_action_open_id_connection(
        aws_profile=config.github_action_open_id_connection.aws_profile,
        stack_name=config.github_action_open_id_connection.stack_name,
        github_org=config.github_action_open_id_connection.github_org,
        github_repo=config.github_action_open_id_connection.github_repo,
        role_name=config.github_action_open_id_connection.role_name,
    )
