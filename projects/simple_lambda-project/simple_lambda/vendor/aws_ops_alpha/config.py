# -*- coding: utf-8 -*-

import typing as T
import dataclasses


@dataclasses.dataclass
class AwsOpsAlphaConfig:
    """
    The aws ops configuration of your project.

    :param env_aws_profile_mapper: for example,
        ``{"devops": "my_devops_profile", "sbx": "my_sbx_profile", "tst": "my_tst_profile", "prd": "my_prd_profile"}``
    """

    env_aws_profile_mapper: T.Dict[str, str] = dataclasses.field(default_factory=dict)
