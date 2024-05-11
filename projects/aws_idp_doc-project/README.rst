Welcome to ``aws_idp_doc`` Documentation
==============================================================================
This is the main documentation for AWS Intelligent Document Processing Solution. It gives you an overview about this solution and will walk you through all sub-projects.

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
