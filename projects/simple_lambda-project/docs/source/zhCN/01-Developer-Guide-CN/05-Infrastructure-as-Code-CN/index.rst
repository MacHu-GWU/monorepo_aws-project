Infrastructure as Code (CN)
==============================================================================
todo


The ``cdk`` folder
------------------------------------------------------------------------------
``cdk`` 目录是 AWS CDK 官方推荐的目录结构. 用于存放 CDK declaration 代码. 然后你就可以在这个目录中 (cd 进去) 运行 ``cdk deploy`` 命令进行部署了. 官网的例子中所有的 declaration 都在 ``app.py`` 一个模块中. 在企业项目中, 最好是将这些 CDK declaration 以一个模块的形式放在你的 App 代码中, 并且将 AWS Resources 按照逻辑分散到不同模块中. 然后在 ``cdk/app.py`` 中 import 它们即可.


The ``simple_lambda/iac/`` Python Modules
------------------------------------------------------------------------------
所有的 IAC 代码都在 ``simple_lambda/iac/`` 模块下. 下面我们列出了所有与 IAC 相关的重要的文件::

    simple_lambda/iac/ # the root folder of the infrastructure as code source code
    simple_lambda/iac/define/ # CDK stack declaration code
    simple_lambda/iac/define/main.py # centralized CDK stack object, AWS resources are break down into sub-modules
    simple_lambda/iac/define/iam.py # IAM related AWS resources
    simple_lambda/iac/define/lbd.py # Lambda function related AWS resources
    simple_lambda/iac/exports.py # CDK stack output exports for other projects to use
    # CDK stack output exports for other projects to use
    tests/iac/test_iac_define.py # the unit test for CDK stack declaration
    tests_int/iac/test_iac_exports.py # the integration test for deployed CDK stack output exports


CDK Stack Declaration
------------------------------------------------------------------------------
所有的 CDK Stack 的声明代码都放在了 ``simple_lambda/iac/define/`` 目录下. 其中 ``main.py`` 是 entry point. 由于我们将不同的 AWS 资源分散到了不同的子模块中, 我们可以通过 comment in / out 来控制是部署部分资源还是部署所有资源.

.. dropdown:: simple_lambda/iac/define/main.py

    .. literalinclude:: ../../../../simple_lambda/iac/define/main.py
       :language: python
       :linenos:


Deploy CDK Stack
------------------------------------------------------------------------------
你可以在本地运行 ``make deploy-app`` 命令来部署 CDK Stack.


CDK Stack Output Exports
------------------------------------------------------------------------------
在微服务架构的最佳实践中, 我们尽可能的将大型系统分拆成较小的 App. 那么 App 之间互相获得对方的 metadata 必须要解决的问题. 例如一个 App 里有一些服务, 但是其他的 App 如何知道这个服务的 endpoint url 是什么呢?

`AWS CloudFormation Output Exports <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html>`_ 是 AWS 原生的一个 feature, 能将 Infrastructure as code 的 value export 给任何需要的人. 所以在本项目中, 我们使用 CloudFormation Output Exports 作为 App 之间互相拉取 metadata 的机制.

在本项目中, 除了 IAC 的 declaration code, 还有一个专门的 ``exports.py`` 模块. 它是一个零依赖即可 import 的模块, 可以直接被复制粘贴到其他项目中使用, 并提供了一套简单的 API 来获得属于本项目的 CloudFormation Output Exports. 这个模块应由本项目的开发者负责维护, 而不是让使用者自己开发一套代码. 在企业项目实践中, 经常会出现 A 找 B 要 Output Exports value, 然后 B 给 A 解释应该怎么怎么做, 然后让 A 自己写代码实现, 这是一个非常坏的模式. 首先, 这个 CDK Stack 是 B 的项目, 也是 B 来维护的, B 最清楚该怎么做. 另外 B 可能会随时修改这个 Stack 的代码, 那么 A 是不可能立刻知道 B 做了哪些改动, 应该配合做哪些修改. 最后如果有很多人都需要依赖 B 的 Output Exports value, 那么维护这些 output 的稳定性就是一个必须要解决的问题, 并且一个个的去教其他人怎么用也是一个很麻烦的工作. 而如果 B 自己维护一个模块, 同时保证这个模块的 API 稳定, 其他人只需要复制粘贴并且 import 即可. 这样减少了沟通成本, 增加了系统稳定性, 同时出了任何问题责任的边界也很清楚.

.. literalinclude:: ../../../../simple_lambda/iac/exports.py
   :language: python
   :linenos:


IAC Development Workflow
------------------------------------------------------------------------------
如果你需要对 CDK 模块进行修改, 推荐你按照下列顺序进行操作:

1. 在 ``simple_lambda/iac/`` 模块中进行开发.
2. 运行 ``tests/iac/test_iac_define.py`` 单元测试确保你的 CDK stack declaration 代码没有错误.
3. 运行 ``make deploy-app`` 命令将 CDK Stack 部署到 sandbox 环境中.
4. 运行 ``tests_int/iac/test_iac_exports.py`` 测试 stack output exports.
