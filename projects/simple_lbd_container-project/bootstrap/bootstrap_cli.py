# -*- coding: utf-8 -*-

"""
A thin wrapper of ``cdk deploy`` and ``cdk destroy`` command, it prints
additional information, and cd to the right directory before doing so.
"""

import dataclasses
import subprocess

import fire
from pathlib_mate import Path
from boto_session_manager import BotoSesManager

# **replace the AWS profile to the one you want to use**
bsm = BotoSesManager(profile_name="bmt_app_devops_us_east_1")
dir_bootstrap = Path.dir_here(__file__)


@dataclasses.dataclass
class Context:
    dir_bootstrap: Path
    deployment_unit_folder: str
    aws_account_id: str
    aws_region: str
    account_alias: str

    @classmethod
    def get(cls, bsm: BotoSesManager):
        response = bsm.iam_client.list_account_aliases()
        account_alias = response.get("AccountAliases", ["Unknown"])[0]
        deployment_unit_folder = dir_bootstrap.parent.name
        return cls(
            dir_bootstrap=dir_bootstrap,
            deployment_unit_folder=deployment_unit_folder,
            aws_account_id=bsm.aws_account_id,
            aws_region=bsm.aws_region,
            account_alias=account_alias,
        )

    def cdk_deploy(self):
        print(
            f"🚀 You are deploying to Deployment Unit ({self.deployment_unit_folder!r}) "
            f"CI/CD stack to AWS Account {self.aws_account_id} (alias: {self.account_alias!r}), "
            f"Region = {self.aws_region}."
        )
        answer = input("Do you want to continue [y/n]: ")
        if answer.lower() != "y":
            exit(0)

        with self.dir_bootstrap.temp_cwd():
            args = ["cdk", "deploy", "--require-approval", "never"]
            subprocess.run(args, check=True)

    def cdk_destroy(self):
        print(
            f"🔥 You are destroying Deployment Unit ({self.deployment_unit_folder!r}) "
            f"CI/CD stack from AWS Account {self.aws_account_id} (alias: {self.account_alias!r}), "
            f"Region = {self.aws_region}."
        )
        answer = input("Do you want to continue [y/n]: ")
        if answer.lower() != "y":
            exit(0)

        with self.dir_bootstrap.temp_cwd():
            args = ["cdk", "destroy", "--force"]
            subprocess.run(args, check=True)


class Command:
    """
    CLI interface to deploy / delete bootstrap CDK stack
    """

    def deploy(self):
        """
        Deploy bootstrap CDK stack
        """
        context = Context.get(bsm=bsm)
        context.cdk_deploy()

    def delete(self):
        """
        Delete bootstrap CDK stack
        """
        context = Context.get(bsm=bsm)
        context.cdk_destroy()


def run():
    fire.Fire(Command)


if __name__ == "__main__":
    run()
