# -*- coding: utf-8 -*-

from urllib import request

url = "https://checkip.amazonaws.com"


def get_public_ip() -> str:
    with request.urlopen(url) as response:
        return response.read().decode("utf-8").strip()

