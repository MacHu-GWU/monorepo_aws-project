# -*- coding: utf-8 -*-

import typing as T
import os

from boto_session_manager import BotoSesManager
from cross_aws_account_iam_role.api import (
    IamRootArn,
    IamUserArn,
    IamRoleArn,
    Grantee,
    Owner,
    deploy,
)
from ..config_init import config


def create_grantee_and_owners() -> T.Tuple[Grantee, T.List[Owner]]:
    _mapper = {
        "root": IamRootArn,
        "user": IamUserArn,
        "role": IamRoleArn,
    }

    devops_aws_account = config.cross_account_iam_permission.devops_aws_account
    workload_aws_accounts = config.cross_account_iam_permission.workload_aws_accounts

    grantee_bsm = BotoSesManager(profile_name=devops_aws_account.aws_profile)
    iam_arn = _mapper[devops_aws_account.grantee.type](
        account=grantee_bsm.aws_account_id, **devops_aws_account.grantee.kwargs
    )
    grantee = Grantee(
        bsm=grantee_bsm,
        stack_name=devops_aws_account.stack_name,
        iam_arn=iam_arn,
        policy_name=devops_aws_account.grantee_policy_name,
    )

    owner_list = list()
    for workload_aws_account in workload_aws_accounts:
        # owner_bsm = BotoSesManager(profile_name=workload_aws_account.aws_profile)
        # if owner_bsm.aws_account_id != workload_aws_account.aws_account_id:
        #     raise ValueError(
        #         f"the aws account id of aws profile {workload_aws_account.aws_profile!r} "
        #         f"doesn't match aws account id {workload_aws_account.aws_account_id!r}"
        #     )
        owner = Owner(
            bsm=BotoSesManager(profile_name=workload_aws_account.aws_profile),
            stack_name=workload_aws_account.stack_name,
            role_name=workload_aws_account.owner_role_name,
            policy_name=workload_aws_account.owner_policy_name,
            policy_document=workload_aws_account.owner_policy_document,
        )
        owner.grant(grantee)
        owner_list.append(owner)
    return grantee, owner_list


def main():
    grantee, owner_list = create_grantee_and_owners()

    deploy(
        grantee_list=[grantee],
        owner_list=owner_list,
    )
