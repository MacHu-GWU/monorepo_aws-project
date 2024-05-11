Welcome to ``aws_idp_data_store`` Documentation
==============================================================================
该项目是 ``aws_idp`` 项目中的一个子模块, 实现了 `Data Store <https://bmt-app-devops-us-east-1-doc-host.s3.amazonaws.com/projects/monorepo_aws/aws_idp_doc/latest/03-Data-Store/index.html>`_ 中提到的模块.

该项目的核心逻辑是在 `aws_textract_pipeline <https://github.com/MacHu-GWU/aws_textract_pipeline-project>`_ 开源项目中维护着的, 本项目只是将核心逻辑和 AWS Lambda 进行了适配.

For first time user, please run the following command to build project documentation website and read it::

    # create virtualenv
    make venv-create

    # install all dependencies
    make install-all

    # build documentation website locally
    make build-doc

    # view documentation website in browser
    make view-doc

If you are experiencing any difficulty to build the documentation website, you can read the document at ``./docs/source/01-Developer-Guide``.
