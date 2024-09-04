# -*- coding: utf-8 -*-

from simple_deploy_gate.logger import logger
from simple_deploy_gate.lbd.hello import low_level_api


def _test_low_level_api():
    # invoke api
    response = low_level_api(name="alice")
    # validate response
    assert response["message"] == "hello alice"


def test_low_level_api():
    with logger.disabled(
        disable=True,
        # disable=False,
    ):
        _test_low_level_api()


if __name__ == "__main__":
    from simple_deploy_gate.tests import run_cov_test

    run_cov_test(__file__, "simple_deploy_gate.lbd.hello", preview=False)
