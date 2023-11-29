# -*- coding: utf-8 -*-

import typing as T

from boto_session_manager import BotoSesManager

from ..config_init import config
from ..cross_account_iam_role_access_manager import (
    IamRootArn,
    IamGroupArn,
    IamUserArn,
    IamRoleArn,
    T_IAM_ARN,
    Grantee,
    Owner,
    deploy,
    get_account_info,
    validate,
    delete,
)


def create_grantee_and_owners() -> T.Tuple[Grantee, T.List[Owner]]:
    _mapper = {
        "root": IamRootArn,
        "group": IamGroupArn,
        "user": IamUserArn,
        "role": IamRoleArn,
    }

    devops_aws_account = config.cross_account_iam_permission.devops_aws_account
    workload_aws_accounts = config.cross_account_iam_permission.workload_aws_accounts

    grantee_bsm = BotoSesManager(profile_name=devops_aws_account.aws_profile)
    klass: T_IAM_ARN = _mapper[devops_aws_account.grantee.type]
    iam_arn = klass(
        account=grantee_bsm.aws_account_id, **devops_aws_account.grantee.kwargs
    )
    grantee = Grantee(
        bsm=grantee_bsm,
        stack_name=devops_aws_account.stack_name,
        iam_arn=iam_arn,
        policy_name=devops_aws_account.grantee_policy_name,
        test_bsm=grantee_bsm,
    )

    owner_list = list()
    for workload_aws_account in workload_aws_accounts:
        owner_bsm = BotoSesManager(profile_name=workload_aws_account.aws_profile)
        if owner_bsm.aws_account_id != workload_aws_account.aws_account_id:
            raise ValueError(
                f"the aws account id of aws profile {workload_aws_account.aws_profile!r} "
                f"doesn't match aws account id {workload_aws_account.aws_account_id!r}"
            )
        owner = Owner(
            bsm=owner_bsm,
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

    def call_api(bsm: BotoSesManager):
        account_id, account_alias, arn = get_account_info(bsm)
        print(
            f"    now we are on account {account_id} ({account_alias}), using principal {arn}"
        )

    validate(
        grantee_list=[grantee],
        call_api=call_api,
    )
