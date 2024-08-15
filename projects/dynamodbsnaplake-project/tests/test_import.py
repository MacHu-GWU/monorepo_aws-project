# -*- coding: utf-8 -*-

import os
import pytest
import dynamodbsnaplake


def test_import():
    _ = dynamodbsnaplake


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
