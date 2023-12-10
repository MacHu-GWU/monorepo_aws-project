.. I am trying to explain the purpose of this folder

Bootstrap the monorepo AWS project
==============================================================================
Scripts in this folder are used to setup the necessary AWS resources for monorepo AWS project, using GitHub Action for CI/CD.

It assumes that:

1. You have multiple deployment units (projects) in the same github repo, partitioned by folder. If you only have one deployment unit, you can still use this and just maintain the folder structure.
2. You have multiple workload AWS accounts for different environments, e.g. sandbox, test, production. It's OK that those workload accounts are actually the same account, separated by naming convention.

There are two types of setups:

1. Multiple environments such as sbx, tst, and prd are deployed to different AWS accounts.
2. Multiple environments such as sbx, tst, and prd are deployed to the same AWS account, and they are softly isolated by a naming convention like ``${project_name}-{env_name}``.

1. Multiple environments such as sbx, tst, and prd are deployed to different AWS accounts.
2. Multiple environments such as sbx, tst, and prd are deployed to the same AWS account, and they are softly isolated by a naming convention like ``${project_name}-{env_name}``.


Run Book
------------------------------------------------------------------------------
In this section, we will explain how to bootstrap the monorepo AWS project.


Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Have an AWS Organization, it should have at least one devops AWS account and three workload AWS Accounts (sandbox, test, production).
    - The "devops" account for your CI/CD resources like CodeCommit repository, CodeBuild project, CodePipeline pipeline,  and code artifacts like deployment package, docker image.
    - It's OK to have arbitrary many workload AWS accounts, like sandbox, dev, test, staging, QA, production, etc ...
    - The "devops" account and "workload" accounts could be the same AWS Account, but it's not recommended.
    - The sbx, tst and prd accounts could be the same account.
2. Have an GitHub Repo, based on the number of workload AWS accounts you are using, create the following secrets in GitHub action "Settings -> Security -> Secrets and variables -> Repository secrets":
    - ``DEVOPS_AWS_ACCOUNT_ID``: the devops aws account id
    - ``SBX_AWS_ACCOUNT_ID``: the sandbox aws account id
    - ``TST_AWS_ACCOUNT_ID``: the test aws account id
    - ``PRD_AWS_ACCOUNT_ID``: the production aws account id


Run
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Then run the following script using the command ``python /path/to/file_name.py`` in sequence. Any Python>=3.8 is OK, it doesn't have to be the virtualenv Python, it will find the virtualenv Python automatically.

1. `s1_setup_venv.py <./s1_setup_venv.py>`_:
2. `s2_cdk_bootstrap.py <./s2_cdk_bootstrap.py>`_:
3. `s3_setup_github_action_oidc.py <./s3_setup_github_action_oidc.py>`_:
4. `s4_setup_cross_account_permission.py <./s4_setup_cross_account_permission.py>`_:
5. `s5_setup_cross_account_s3_bucket_permission.py <./s5_setup_cross_account_s3_bucket_permission.py>`_:
