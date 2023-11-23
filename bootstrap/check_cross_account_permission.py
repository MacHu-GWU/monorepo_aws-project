# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager

bsm = BotoSesManager()

bsm.assume_role(role_arn="arn:aws:iam::123456789012:role/role-name")
