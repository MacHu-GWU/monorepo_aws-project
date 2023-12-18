About the ``bin`` folder
==============================================================================
The ``bin`` folder (bin stands for binary) is a Linux convention that stores the executable scripts.

Folder structure::

- ``automation``: stores python automation code to create the initial virtualenv and install dependencies for project, even without virtualenv and poetry installed at beginning.
- ``requirements-jumpstart.txt``: used by ``automation``, you don't have to install it manually, the automation code will automatically install it.
- ``s00, 01, ..., scripts are common devops steps automation script``. You can either run them as a python script, or use the ``make`` command to run time. These scripts are also used in the CI/CD pipeline.
