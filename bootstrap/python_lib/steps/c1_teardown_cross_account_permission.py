# -*- coding: utf-8 -*-

from cross_aws_account_iam_role.api import (
    delete,
)
from .s4_setup_cross_account_permission import create_grantee_and_owners


def main():
    grantee, owner_list = create_grantee_and_owners()

    delete(
        grantee_list=[grantee],
        owner_list=owner_list,
    )
