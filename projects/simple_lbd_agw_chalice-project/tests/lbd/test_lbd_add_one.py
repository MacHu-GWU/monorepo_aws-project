# -*- coding: utf-8 -*-

import moto
from pynamodb.connection import Connection

from simple_lbd_agw_chalice.logger import logger
from simple_lbd_agw_chalice.lbd.add_one import Counter, low_level_api
from simple_lbd_agw_chalice.tests.mock_aws import BaseMockAws


class Test(BaseMockAws):
    mock_list = [
        moto.mock_sts,
        moto.mock_dynamodb,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        Connection()
        Counter.create_table(wait=True)

    def _test_low_level_api(self):
        key = "test"
        counter = Counter(key=key)

        low_level_api(key=key)
        counter.refresh()
        assert counter.count == 1

        low_level_api(key=key)
        counter.refresh()
        assert counter.count == 2

    def test_low_level_api(self):
        with logger.disabled(
            disable=True,
            # disable=False,
        ):
            self._test_low_level_api()


if __name__ == "__main__":
    from simple_lbd_agw_chalice.tests import run_cov_test

    run_cov_test(__file__, "simple_lbd_agw_chalice.lbd.add_one", preview=False)
