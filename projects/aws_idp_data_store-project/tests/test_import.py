# -*- coding: utf-8 -*-

import os
import pytest
import aws_idp_data_store


def test_import():
    _ = aws_idp_data_store


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
