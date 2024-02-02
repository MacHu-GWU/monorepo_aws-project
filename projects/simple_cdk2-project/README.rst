Welcome to ``simple_cdk2`` Documentation
==============================================================================
This is a sample project that demonstrates the best practices for a production ready AWS CDK project that depends on other CloudFormation stack. In this project, it creates an IAM Role that uses a Managed IAM Policy from other project (CDK Stack). It is also a project template can be used to create more project like "this".

For first time user, please run the following command to build project documentation website and read it::

    # create virtualenv
    make venv-create

    # install all dependencies
    make install-all

    # build documentation website locally
    make build-doc

    # view documentation website in browser
    make view-doc
