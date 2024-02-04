# -*- coding: utf-8 -*-

"""
Batch remove docker images from local.
"""

import subprocess

image_id_list = """
a1b2c3d4e5f6
g1h2i3j4k5l6
m1n2o3p4q5r6
s1t2u3v4w5x6
""".strip().splitlines()
for image_id in image_id_list:
    args = [
        "docker",
        "image",
        "rm",
        image_id,
        "-f",
    ]
    print(args)
    subprocess.run(args)
