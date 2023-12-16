About ``bootstrap`` Folder
==============================================================================
In a "single repo", "multi deployment units" Git repository setup, each deployment unit has its own `CodeBuild project <https://docs.aws.amazon.com/codebuild/latest/userguide/working-with-build-projects.html>`_ to run CI (Continue Integration) logic and a `CodePipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html>`_ to run CD (Continue Deployment) logic. Therefore, every deployment unit has a bootstrap folder to provision these resources. Everytime you start a new deployment unit project, you should do ``bootstrap`` first to provision necessary AWS resources for CI/CD.


CI/CD Resources for each Deployment Unit
------------------------------------------------------------------------------
Below is the list of resources that will be provisioned for each deployment unit:

- An AWS `Lambda Function <https://docs.aws.amazon.com/lambda/latest/dg/welcome.html>`_ that receives CodeCommit event, analyze it and decide to run (or not run) which CodeBuild project.
- An `IAM Role <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html>`_ for the above Lambda Function.
- An AWS `Event Rule <https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rules.html>`_ that captures CodeCommit reference create / update (create, update branch, push commits) events, filter it based on branch name, and trigger the above Lambda Function.
- An AWS `CodeBuild Project <https://docs.aws.amazon.com/codebuild/latest/userguide/working-with-build-projects.html>`_ that runs CI logic.
- An IAM Role for the above CodeBuild Project.
- An AWS `CodePipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html>`_ that runs CD logic.
- An IAM Role for the above CodePipeline.

For this AWS Batch project, we need additional CI/CD resources:

- an IAM role for container running in CodeBuild. Since the container for ``docker build`` in CodeBuild is another isolated environment, not the codebuild runtime, it doesn't inherit the codebuild runtime IAM permission. Based on the official blog post, we should let the codebuild runtime role to assume another role, and pass the assumed credentials to the container runtime via ``docker build`` command. And the this role is the assumed role for container running in CodeBuild.


Files in this Folder Walkthrough
------------------------------------------------------------------------------
Let's take a look at the files in this folder:


Deployment Unit Config ``du-config.json``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This config files defines the CI/CD related configurations.

.. code-block:: javascript

    {
        // deployment unit name, this is the git branch prefix that triggers the CI/CD
        "du_name": "simple_batch",
        // this is the sub-folder name of your deployment unit, the relative path to
        // git repo root dir should be "projects/${du_folder}/"
        // it has to have a buildspec.yml file in it.
        "du_folder": "simple_batch-project",
        // this is the common prefix for all the AWS resource name for this deployment unit
        // the full prefix is actually "${repo_name_prefix}-${du_name_prefix}"
        // where the ${repo_name_prefix} is defined in the "shared/repo-config.json" file
        "du_name_prefix": "simple_batch"
    }


``app.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is the CDK code. It declare the resources mentioned in the "CI/CD Resources for each Deployment Unit" section.


``bootstrap_cli.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It is a CLI tool to provision or delete CI/CD AWS Resources. It is a wrapper of ``cdk ...`` command. It requires some Python dependencies, but you don't have to install them yourself, we have another automation script that wraps around this script and automates the creation of virtualenv and installing dependencies.

I don't recommend running it directly. Run it only if you understand what it is doing.


``bootstrap_lib.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It is a wrapper of ``bootstrap_cli.py``, automates the creation of virtualenv and installing dependencies. This script has zero dependencies.

I don't recommend running it directly. Run it only if you understand what it is doing.


``bootstrap.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Automation script to run bootstrap, just run it with Python3.7+::

    python bootstrap.py


``teardown.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Automation script to run teardown, just run it with Python3.7+::

    python teardown.py


``cdk_deploy.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It is an automation script to deploy the shared CDK stack. Basically it is a wrapper of CLI command ``cdk deploy ...``.


``codebuild_trigger_lambda/lambda_function.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is the CodeBuild project trigger lambda function source code. It receives CodeCommit git repository events and trigger the CodeBuild project accordingly. You can customize it to define your own triggering rules.


``build_lambda_source.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This automation script can build the lambda function deployment package zip file. It will be invoked in the ``app.py`` script.


``requirements.txt``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This file includes the required dependencies to run the ``cdk deploy...`` command. If you don't want to use the ``cdk_deploy.py`` automation script and prefer to run the ``cdk deploy...`` command manually, the dependencies listed in this file should be sufficient.


Run Bootstrap
------------------------------------------------------------------------------
Everytime when you create a new deployment unit project, you should run the ``python cdk_deploy.py`` script to provision necessary AWS resources for CI/CD::

    cd projects/${du_folder}/bootstrap
    python bootstrap.py

If you want to delete CI/CD AWS Resources, you can do::

    cd projects/${du_folder}/bootstrap
    python teardown.py


Next Step
------------------------------------------------------------------------------
至此你已经成功地为你的 Deployment Unit 项目创建了所需的 CI/CD 资源了. 你可以开始进行项目开发了. 在开始写 Code 之前, 推荐你阅读 ``${du_folder}/README.rst`` 中的开发者指南, 学习如何进行该项目的开发.
You just successfully created necessary CI/CD AWS Resources for your deployment unit. Before writing any code, I suggest reading the developer guide in ``projects/${du_folder}/README.rst`` for more details about software development life cycle (SDLC) workflow.
