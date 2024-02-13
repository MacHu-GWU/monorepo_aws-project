Infrastructure as Code
==============================================================================
Infrastructure as Code (IAC) is the managing and provisioning of infrastructure through code instead of through manual processes. It is a critical piece for building applications on cloud. There are lots of IAC tools, such as `AWS CDK <https://aws.amazon.com/cdk/>`_, `CloudFormation <https://aws.amazon.com/cloudformation/>`_, `terraform <https://www.terraform.io/>`_, `pulumi <https://www.pulumi.com/>`_, etc ... You can use any of them that you feel most comfortable with. In this project, we use CDK, the most AWS Cloud native tool, to implement the IAC.

Next, let's walkthrough the code that is related to IAC.


The ``cdk`` folder
------------------------------------------------------------------------------
The ``cdk`` folder is the CDK official convention where you should store your IAC declaration code and where you should run the ``cdk deploy`` command. However, for enterprise project, we should break down complicated logics into modules for better maintainability. The ``cdk/app.py`` script just import the declaration code from the ``simple_lambda/iac/`` Python modules.


The ``simple_lambda/iac/`` Python Modules
------------------------------------------------------------------------------
``simple_lambda/iac/`` is the root folder of the infrastructure as code source code. Below are the list of important files related to Infrastructure as Code::

    simple_lambda/iac # the root folder of the infrastructure as code source code
    simple_lambda/iac/define/ # CDK stack declaration code
    simple_lambda/iac/define/main.py # centralized CDK stack object, AWS resources are break down into sub-modules
    simple_lambda/iac/define/iam.py # IAM related AWS resources
    simple_lambda/iac/define/lbd.py # Lambda function related AWS resources
    simple_lambda/iac/exports.py # CDK stack output exports for other projects to use
    tests/iac/test_iac_define.py # the unit test for CDK stack declaration
    tests_int/iac/test_iac_exports.py # the integration test for deployed CDK stack output exports


CDK Stack Declaration
------------------------------------------------------------------------------
The ``main.py`` is a module to choose what IAC module you want to includes. It just import other IAC modules.

.. literalinclude:: ../../../../simple_lambda/iac/define/main.py
   :language: python
   :linenos:

The ``iam.py`` is a IAC module that includes the AWS IAM related resources. Of course you can have more IAC modules like this.

.. literalinclude:: ../../../../simple_lambda/iac/define/iam.py
   :language: python
   :linenos:

The ``exports.py`` module can be copied to other projects to access IAC output values.

.. literalinclude:: ../../../../simple_lambda/iac/define/exports.py
   :language: python
   :linenos:


Deploy CDK Stack
------------------------------------------------------------------------------
You can run ``make deploy-app`` locally to deploy CDK Stack.


CDK Stack Output Exports
------------------------------------------------------------------------------
todo


IAC Development Workflow
------------------------------------------------------------------------------
1. Working on ``simple_lambda/iac/`` module to declare your CDK stack.
2. Run ``tests/iac/test_iac_define.py`` to test your CDK stack declaration.
3. Run ``make deploy-app`` to deploy your CDK stack to sandbox environment.
4. Run ``tests_int/iac/test_iac_exports.py`` to test your CDK stack output exports.
