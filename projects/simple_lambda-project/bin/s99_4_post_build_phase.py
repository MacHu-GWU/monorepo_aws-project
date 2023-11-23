# -*- coding: utf-8 -*-

# helpers
from automation.logger import logger
from automation.emoji import Emoji


@logger.start_and_end(
    msg="Post Phase",
    start_emoji=f"{Emoji.start} {Emoji.post_build_phase}",
    end_emoji=Emoji.post_build_phase,
    pipe=Emoji.post_build_phase,
)
def post_build_phase():
    """
    Note that this phase is always run even if the build phases fail.

    Reference:

    - Build phase transitions: https://docs.aws.amazon.com/codebuild/latest/userguide/view-build-details.html#view-build-details-phases
    """
    pass


post_build_phase()
