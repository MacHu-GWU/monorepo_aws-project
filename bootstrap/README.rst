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

    python s1_setup_venv.py
    python s2_cdk_bootstrap.py
    python s3_setup_cross_account_permission.py


Prerequisites:

1. Have an AWS Organization, it should have at least "one" plus "three" AWS Accounts.
    - The "one" is called "devops" account for your CI/CD resources like CodeCommit repository, CodeBuild project, CodePipeline pipeline, etc.
    - The "three" are "workload" accounts like sbx, tst, and prd.
    - The "devops" account and "workload" accounts could be the same.
    - The sbx, tst and prd accounts could be the same account.

1. s1_setup_venv.py:
2. s2_cdk_bootstrap.py:
3. s3_setup_cross_account_permission.py: