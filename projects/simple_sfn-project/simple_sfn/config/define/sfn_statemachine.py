# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from boltons.strutils import slugify, under2camel
from ...vendor.import_agent import aws_ops_alpha

from ...constants import LIVE

if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager
    from .main import Env


@dataclasses.dataclass
class StateMachine:
    env: "Env" = dataclasses.field(init=False)
    short_name: T.Optional[str] = dataclasses.field(default=None)
    live_version1: T.Optional[str] = dataclasses.field(default=None)
    live_version2: T.Optional[str] = dataclasses.field(default=None)
    live_version2_percentage: T.Optional[int] = dataclasses.field(default=None)

    @property
    def name(self) -> str:
        """
        Full name of the State Machine.
        """
        return f"{self.env.project_name_snake}-{self.env.env_name}-{self.short_name}"

    @property
    def short_name_slug(self) -> str:
        """
        Example: ``my-state-machine``.
        """
        return slugify(self.short_name, delim="-")

    @property
    def short_name_snake(self) -> str:
        """
        Example: ``my_state_machine``.
        """
        return slugify(self.short_name, delim="_")

    @property
    def short_name_camel(self) -> str:
        """
        The state machine short name in camel case. This is usually used
        in CloudFormation logic ID.

        Example: ``MyStateMachine``.
        """
        return under2camel(slugify(self.short_name, delim="_"))

    @property
    def log_group_name(self) -> str:
        """
        The State Machine CloudWatch log group name
        """
        return f"/aws/vendedlogs/states/{self.name}-Logs"

    @property
    def arn(self) -> str:
        return f"arn:aws:states:{self.env.aws_region}:{self.env.aws_account_id}:stateMachine:{self.name}"

    # @property
    # def target_live_version1(self) -> str:
    #     """
    #     Get the lambda version you want to set as ALIAS 'LIVE'.
    #     If the live version is not specified, use the '$LATEST' version.
    #     :return:
    #     """
    #     return aws_ops_alpha.aws_stepfunction_version_and_alias.deploy_alias() if self.live_version1 is None else self.live_version1

    def publish_version(
        self,
        bsm: "BotoSesManager",
    ) -> T.Tuple[bool, int]:  # pragma: no cover
        """
        Publish a new version. This API is idempotent, i.e. if the $LATEST
        version is already the latest published version, then nothing will happen.

        :param bsm: workload boto session manager.

        :return: a tuple of two items, first item is a boolean flag to indicate
            that if a new version is created. the second item is the version number.
        """
        return aws_ops_alpha.aws_stepfunction_version_and_alias.publish_version(
            bsm.sfn_client,
            state_machine_arn=self.arn,
        )

    def deploy_alias(
        self,
        bsm: "BotoSesManager",
    ) -> T.Tuple[bool, T.Optional[T.Dict[int, int]]]:  # pragma: no cover
        """
        Set the given alias to the given version. If the alias does not exist, create it.

        :param bsm: workload boto session manager.

        :return: a tuple of two items; first item is a boolean flag to indicate
            whether a creation or update is performed; second item is the alias
            revision id, if creation or update is not performed, then return None.
        """
        return aws_ops_alpha.aws_stepfunction_version_and_alias.deploy_alias(
            sfn_client=bsm.sfn_client,
            state_machine_arn=self.arn,
            alias=LIVE,
            version1=self.live_version1,
            version2=self.live_version2,
            version2_percentage=self.live_version2_percentage,
        )


@dataclasses.dataclass
class StateMachineMixin:
    state_machines: T.Dict[str, StateMachine] = dataclasses.field(default_factory=dict)

    @property
    def state_machine_name_list(self) -> T.List[str]:
        """
        Example::

            >>> StateMachineMixin().state_machine_name_list
            [
                '${project_name}-${env_name}-${short_name1}',
                '${project_name}-${env_name}-${short_name2}',
                '${project_name}-${env_name}-${short_name3}',
            ]
        """
        return [state_machine.name for state_machine in self.state_machines.values()]

    @property
    def state_machine_list(self) -> T.List[StateMachine]:
        """
        :class:`StateMachine` object list.
        """
        return list(self.state_machines.values())

    # --------------------------------------------------------------------------
    # Enumerate State Machines
    # --------------------------------------------------------------------------
    @property
    def sm_run_job(self) -> StateMachine:
        return self.state_machines["run_job"]
