Welcome to ``aws_idp_doc`` Documentation
==============================================================================
该项目是 ``aws_idp`` 项目中的一个子模块, 实现了 `Data Store <https://bmt-app-devops-us-east-1-doc-host.s3.amazonaws.com/projects/monorepo_aws/aws_idp_doc/latest/03-Data-Store/index.html>`_ 中提到的模块.

For doc maintainer, please run the following command to build project documentation website and read it::

    # create virtualenv
    make venv-create

    # install all dependencies
    make install-all

    # build documentation website locally
    make build-doc

    # view documentation website in browser
    make view-doc

    # Deploy Documentation Site To S3 as Latest Doc
    make deploy-latest-doc

    # View latest documentation website on S3
    make view-latest-doc
