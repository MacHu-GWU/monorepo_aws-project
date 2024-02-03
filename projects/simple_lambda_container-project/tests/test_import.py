# -*- coding: utf-8 -*-

import os
import pytest
import simple_lambda_container


def test_import():
    _ = simple_lambda_container


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
