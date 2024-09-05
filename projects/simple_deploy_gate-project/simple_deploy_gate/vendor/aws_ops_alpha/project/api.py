# -*- coding: utf-8 -*-

"""
Usage example::

    >>> import aws_ops_alpha.project.simple_lambda.api as simple_lambda_project
"""

try:
    from .simple_python import api as simple_python_project
except ImportError:  # pragma: no cover
    pass
try:
    from .simple_cdk import api as simple_cdk_project
except ImportError:  # pragma: no cover
    pass
try:
    from .simple_config import api as simple_config_project
except ImportError:  # pragma: no cover
    pass
try:
    from .simple_lambda import api as simple_lambda_project
except ImportError:  # pragma: no cover
    pass
try:
    from .simple_lbd_container import api as simple_lbd_container_project
except ImportError:  # pragma: no cover
    pass
try:
    from .simple_lbd_agw_chalice import api as simple_lbd_agw_chalice_project
except ImportError:  # pragma: no cover
    pass
try:
    from .simple_glue import api as simple_glue_project
except ImportError:  # pragma: no cover
    pass
try:
    from .simple_sfn import api as simple_sfn_project
except ImportError:  # pragma: no cover
    pass
