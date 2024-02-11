Software Development Life Cycle (SDLC)
==============================================================================
This section assumes that you have an idea but no existing code. The following steps will guide you through creating a new deployment unit project from scratch, starting with development and progressing through various sandbox environments, test environment and finally deploying to the production environment.


1. bootstrap
------------------------------------------------------------------------------
First, let's create a new project code skeleton using a sample project. It will prompt you to enter your project name and some configuration::

    # assume that you are currently at the ``./projects/simple_sfn-project`` directory.
    python ../../cookiecutter/simple_sfn.py

Next, copy the generated project skeleton from the ``./cookiecutter/tmp/template-project/${your_project_name}`` directory to the ``./projects/${your_project_name}`` directory.

Now that you have a new project to work on, the project name is the one you just entered. However, for illustrative purposes, let's assume the project name is also ``simple_sfn`` (``${du_name}``). Please note that all the following documentation is based on this assumption. In your actual project development, make sure to replace the name with your real project name.

Every project requires a collection of AWS resources for CI/CD. To provision these resources, we need to run a script called ``bootstrap``. Please refer to the ``./projects/simple_sfn-project/bootstrap/README.rst`` file for more details. You can use the following command to provision the CI/CD AWS resource::

    # assume that you are currently at the ``./projects/simple_sfn-project`` directory.
    python ./bootstrap/bootstrap.py

Now, you are all set for development and deployment. However, I strongly recommend practicing the CI/CD and deployment process without making any changes to the application's code logic. This practice will help you gain a better understanding of the process and the tools involved.


2. Feature Development
------------------------------------------------------------------------------
In this step, we focus on the core application code logic of the project. From this point, I assume that you are currently at the ``./projects/simple_sfn-project`` (``./projects/${du_name}-project``) directory.

1. Create a feature branch: ``simple_sfn/feature/${description}`` (``${du_name}/feature/${description}``) and start development.
2. This project heavily uses shell script to automate the action in SDLC workflow. It makes the development and deployment process more efficient. In a life time of a development laptop, you only need to install the dependencies for automation just once::

    pip install -r requirements-automation.txt

3. Create a virtualenv for your project. This project use ``make`` command to automate local development on MacOS laptop. You can type ``make`` to see all available commands::

    make venv-create

4. Before installing any dependencies, you need to resolve the version of yor dependencies to ensure the deterministic deployment::

    make poetry-lock

5. Now you can install all the dependencies. The ``make install-all`` command will install all kinds of dependencies. But if you only want to install specific group of dependencies, you could try ``make install``, ``make install-dev``, ``make install-test``, ``make install-doc`` and ``make install-automation``::

    make install-all

6. Activate the virtualenv and start doing development. For first time user, I suggest not changing any application code and focus on learning.

    source .venv/bin/activate

7. Run code coverage test locally and make sure it passes. A decent amount of test coverage ensure the quality of your code. You can also uses the ``make view-cov`` to identify what code is not covered by unit test::

    make cov

8. Every project has a config management system. The local unit test is using the local config data for testing. In CI/CD environment, it will read the config from AWS SSM Parameter store. So we have to deploy the config to AWS SSM Parameter store first::

    make deploy-config

9. Publish your branch to Git, start a merge request, and invite other developer for code review. The feature branch will automatically trigger a Codebuild to run the unit test. You can use ``make info`` command to display lots of useful information and link about your project. For example, you can click the ``codebuild`` link to preview your CI job run status and logging.

10. Now you can merge the ``simple_sfn/feature/${description}`` to ``main``.


3. Publish Expensive Artifacts (layer, container image, etc)
------------------------------------------------------------------------------
Some artifacts are very time consuming to build. We don't want to include that in every CI job run. Since this is a Lambda project, we need to build the Lambda layer to store the dependencies.

1. Create a layer branch ``simple_sfn/layer/${description}`` (``${du_name}/layer/${description}``).
2. Don't do any application code change, focus on the dependencies you defined in the ``pyproject.toml`` file, and use the ``make poetry-lock`` command to resolve the the version of your dependencies. And then run a final check ``make cov`` to ensure that the dependencies are compatible with your application code.
3. Publish your branch to Git, start a merge request, and invite other developer for code review. The layer branch will automatically trigger a Codebuild to run the unit test and publish a new layer version. It is very smart that if the dependencies list are not changed, then it will skip the layer build process.
4. Once you see a new layer is published, you can merge the ``simple_sfn/layer/${description}`` to ``main``.

Note that we only need to build Lambda layer in this project. In other type of project, we may need a different branch to build artifacts like "container image", "ec2 image" etc. But the process is similar.


4. Application logic Unit test, App Deployment and Integration test
------------------------------------------------------------------------------
In this step, we focus deploying the app to ``sandbox`` environment and run integration test.

1. Create a lambda branch ``simple_sfn/lambda/${description}`` (``${du_name}/lambda/${description}``).
2. Implement the CDK code in the ``simple_sfn/iac/`` python module (The code skeleton generated from sample project should be working as it is).
3. Deploy the CDK stack via ``cdk deploy`` command. The following command is a wrapper that will handle a lot of details::

    make deploy-app

4. Implement the integration test code in the ``tests_int/`` folder. And use real AWS Lambda and for testing.

    make int

5. Once the integration test passed on local laptop, you can publish your branch to Git, start a merge request, and invite other developer for code review. The lambda branch will automatically trigger a Codebuild to run the unit test, deploy the app to ``sandbox`` environment and run integration test.

6. Once you see the app is deployed to ``sandbox`` and the integration test is passed, you can merge the ``simple_sfn/lambda/${description}`` to ``main``.


5. Release from sandbox to test and then to production
------------------------------------------------------------------------------
You app is deployed to ``sandbox`` and thoroughly tested. Now it is time to release it to ``test`` and then to ``production``.

1. Create a release branch ``simple_sfn/release`` (``${du_name}/release``). Don't do any application code change in this branch. If you have to, please roll back to the previous step to ensure that your change doesn't break the test.
2. If you have made any change to configuration, please run the ``make deploy-config`` command to update it to the latest.
3. Publish your branch to Git, it will trigger a CodePipeline to deploy the app firstly to ``sandbox``, then ``test`` environment. Then it will pause and wait for your manual approval. Please review the integration test result in the ``test`` environment CodeBuild job run. If everything is good, please approve the release to the ``prod``.


6. (Optional) Clean Up App Deployment and Infrastructure
------------------------------------------------------------------------------
If you want to delete all of the resources created by this project, you can follow the steps below:

1. **Clean up the deployed application**

- Create a cleanup branch: ``simple_sfn/cleanup`` (``${du_name}/cleanup``). Don't do any application code change in this branch.
- Update the chore.txt file, this file is designed to be changed when you want to create a new git commits without changing anything to the application logic. Enter the environment name you want to clean up in the commit message, for example: ``cleanup: sbx, tst, prd``. The commit message has to start with ``cleanup:`` and followed by a comma separated environment name you want to clean up. Because it is a dangerous operation, we want to make sure that you are aware of what you are doing.
- Let the codebuild run to clean up the specified environments. It will delete the  CDK stack.

2. **Clean up CI/CD resource**

- Just go to AWS CloudFormation console and delete the ``multi-env-simple-apigateway-stack`` (``${repo_name_prefix}-${du_name}-stack``) stack.
