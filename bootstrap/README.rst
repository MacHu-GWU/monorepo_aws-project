.. I am trying to explain the purpose of this folder


Bootstrap the monorepo AWS project
==============================================================================
Scripts in this folder are used to setup the necessary AWS resources for monorepo AWS project.

There are two types of setups:

1. Multiple environments such as sbx, tst, and prd are deployed to different AWS accounts.
2. Multiple environments such as sbx, tst, and prd are deployed to the same AWS account, and they are softly isolated by a naming convention like ``${project_name}-{env_name}``.

1. Multiple environments such as sbx, tst, and prd are deployed to different AWS accounts.
2. Multiple environments such as sbx, tst, and prd are deployed to the same AWS account, and they are softly isolated by a naming convention like ``${project_name}-{env_name}``.

.. code-block:: bash

    virtualenv -p python3.9 .venv
    source .venv/bin/activate
    pip install -r requirements.txt

