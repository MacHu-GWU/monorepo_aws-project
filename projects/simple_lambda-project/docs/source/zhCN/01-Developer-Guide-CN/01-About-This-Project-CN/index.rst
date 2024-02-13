About This Project [CN]
==============================================================================
这个项目是一个用来演示我于多年生产实践中总结出的一套用于生产环境中的 AWS Lambda 项目的最佳实践. 里面的业务逻辑虽然非常简单, 但涵盖了生产实践中会遇到的各种挑战. 每当我做新的类似的项目时都会参考这个项目.

同时, 这个项目也是一个 "模板项目", 可以让我只用填写几个名字, 就能生成除了实际业务逻辑以外的所有代码, 使得我能专注于业务逻辑, 而能更快的让项目产生商业价值.

由于这种模板化的设计, 在企业项目管理时, 实现了 "一次设计, 处处收益". 无需所有的团队成员了解项目的所有细节, 新成员只需要能专注于业务逻辑进行开发, 就能快速的交付并产生商业价值.


What is AWS Lambda Project
------------------------------------------------------------------------------
`AWS Lambda <https://aws.amazon.com/lambda/>`_ 允许你无需管理基础设施, 甚至无需管理容器即可运行代码的 Serverless 服务. 它也是 AWS 计算服务中的王牌服务之一.

这个项目假设你的 Lambda Function 的依赖不会超过 250MB, 也就无需构建自定义容器, 使用 Lambda Layer 即可打包依赖. 这个项目使用了 AWS CDK 作为主要的部署工具, 并包含了一整套为这个目的而设计工具链, 包括:

1. 本地开发环境.
2. 本地单元测试工具.
3. Lambda Layer 构建工具.
4. 基础设施即代码部署工具.
5. 多环境部署工具 (sbx, tst, prd).
6. 本地集成测试工具.
7. 中心化的多环境 Config Management 管理工具.
8. CI 自动化构建, 测试, 部署工具.
9. 多环境 CD 自动化部署管道.
10. 生产环境中的 蓝绿部署, 灰度部署, 以及在出现错误时版本回滚工具.

以上的所有工具链都是模块化的工具, 即可以单独拿出来在其他任何项目中使用, 而这个项目中我们已经将这些工具都整合到了一起可以无缝配合使用了.


Business Logic in This Project
------------------------------------------------------------------------------
这个项目主要是为了演示目的. 它包含了两个 Lambda Function:

1. 一个简单的 hello world. 你输入 ``{"name": "alice"}``, 它就会返回 ``{"message": "hello alice"}``.
2. 一个由 S3 event 触发的 lambda function, 他能将文件从一个文件夹自动拷贝到另一个文件夹.

这两种模式分别实现了 "手动运行" 和 "事件驱动运行" 的两种设计模式.


Rule Set
------------------------------------------------------------------------------
**Multi Environment**

在这个项目中, 我们使用了 sbx, tst, prd 三个 workload 环境.

.. dropdown:: simple_lambda/env.py

    .. literalinclude:: ../../../../simple_lambda/env.py
       :language: python
       :linenos:

**Semantic Git Branching**

在这个项目中, 我们使用了 `aws_ops_alpha.api.simple_lambda_project <https://aws-ops-alpha.readthedocs.io/en/latest/zhCN/02-Code-Recipes-CN/04-Rule-Set-Code-Recipe-CN/index.html#simple-lambda-rule-set>`_ 默认的策略.


DevOps CLI Tool
------------------------------------------------------------------------------
当 CD 到 ``simple_lambda-project`` 目录之后, 你可以用 ``make ${command}`` 命令来执行常见的 DevOps Step. 你也可以用 ``make`` 命令列出所有的 Command.

.. code-block::

    help                                     ** Show this help message
    info                                     ** Show Project Information
    venv-create                              ** Create Virtual Environment
    venv-remove                              ** Remove Virtual Environment
    install                                  ** Install main dependencies and Package itself
    install-dev                              Install Development Dependencies
    install-test                             Install Test Dependencies
    install-doc                              Install Document Dependencies
    install-automation                       Install Dependencies for Automation Script
    install-all                              Install All Dependencies
    poetry-export                            Export requirements-*.txt from poetry.lock file
    poetry-lock                              Resolve dependencies using poetry, update poetry.lock file
    show-context-info                        Show Runtime, Environment and Git info
    test                                     ** Run test
    test-only                                Run test without checking test dependencies
    cov                                      ** Run code coverage test
    cov-only                                 Run code coverage test without checking test dependencies
    view-cov                                 View code coverage test result in web browser
    int                                      ** Run integration test
    int-only                                 Run integration test without checking test dependencies
    build-doc                                Build documentation website locally
    build-doc-only                           Build documentation website locally without checking doc dependencies
    view-doc                                 View documentation website locally
    deploy-versioned-doc                     Deploy Documentation Site To S3 as Versioned Doc
    deploy-latest-doc                        Deploy Documentation Site To S3 as Latest Doc
    view-latest-doc                          View latest documentation website on S3
    build-source                             Build Lambda source artifacts
    build-layer                              Build and publish Lambda layer
    deploy-config                            Deploy versioned config data to parameter store backend.
    delete-config                            Delete config data from parameter store backend.
    deploy-app                               Deploy Lambda app via CDK deploy
    delete-app                               Delete Lambda app via CDK destroy
    bump-patch                               Bump patch version
    bump-minor                               Bump minor version
    bump-major                               Bump major version


What's Next
------------------------------------------------------------------------------
从下一篇文档开始, 我们将详细介绍如何使用这个项目模板进行新项目开发的流程. 其中包含了如何创建新项目, 以及如何以一个发布周期作为基本单位进行快速迭代.
