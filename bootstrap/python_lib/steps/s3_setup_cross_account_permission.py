# -*- coding: utf-8 -*-

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


def main():
    _mapper = {
        "root": IamRootArn,
        "group": IamGroupArn,
        "user": IamUserArn,
        "role": IamRoleArn,
    }

    grantee_bsm = BotoSesManager(profile_name=config.devops_aws_account.aws_profile)
    klass: T_IAM_ARN = _mapper[config.devops_aws_account.grantee.type]
    iam_arn = klass(
        account=grantee_bsm.aws_account_id, **config.devops_aws_account.grantee.kwargs
    )
    grantee = Grantee(
        bsm=grantee_bsm,
        iam_arn=iam_arn,
        policy_name=config.devops_aws_account.grantee_policy_name,
        test_bsm=grantee_bsm,
    )

    owner_list = list()
    for environment_aws_account in config.environment_aws_accounts:
        owner_bsm = BotoSesManager(profile_name=environment_aws_account.aws_profile)
        if owner_bsm.aws_account_id != environment_aws_account.aws_account_id:
            raise ValueError(
                f"the aws account id of aws profile {environment_aws_account.aws_profile!r} "
                f"doesn't match aws account id {environment_aws_account.aws_account_id!r}"
            )
        owner = Owner(
            bsm=owner_bsm,
            role_name=environment_aws_account.owner_role_name,
            policy_name=environment_aws_account.owner_policy_name,
            policy_document=environment_aws_account.owner_policy_document,
        )
        owner.grant(grantee)
        owner_list.append(owner)

    deploy(
        grantee_list=[grantee],
        owner_list=owner_list,
        deploy_name=config.cross_account_permission_deploy_name,
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

    # delete(
    #     grantee_list=[grantee],
    #     owner_list=owner_list,
    #     deploy_name=config.cross_account_permission_deploy_name,
    # )
