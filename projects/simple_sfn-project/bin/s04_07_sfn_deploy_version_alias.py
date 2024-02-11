#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simple_sfn.ops import publish_state_machine_version, deploy_state_machine_alias

publish_state_machine_version(check=True)
deploy_state_machine_alias(check=True)
