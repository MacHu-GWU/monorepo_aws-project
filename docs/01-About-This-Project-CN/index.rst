About This Project (CN)
==============================================================================


Why This Project
------------------------------------------------------------------------------
在我的工作中经常要交付各种各样的 AWS 项目, 包括 Infrastructure as Code 项目, AWS Lambda 项目,  API Gateway 项目, AWS Batch 项目, AWS Step Function 项目, AWS ECS Task 项目, AWS Glue ETL 项目, AWS SageMaker ML 项目. 有时这些项目一个个彼此独立. 有的时候这些项目虽然是被独立部署和维护, 但是互相之间有着非常紧密的联系.

在工作中, 我往往要为每一个新的项目创建一个 Git repo, 并且创建 CI/CD 的资源, 搭建基础设施. 但是对于不同的项目往往会选择不同的 CI 工具, 不同的 AWS Account Hierarchy, 不同的项目目录结构. 虽然有着很多的历史经验可以参考, 但是每次做新项目依然有很多前期工作要做.

所以我决定创建一个包含有大量种子项目的 Git repo, 在这个 repo 中预先继承了 CI/CD 的最佳实践. 使得以后我要做任何新项目, 就能迅速地利用模版引擎, 从种子项目中生成新项目的初始代码框架. 然后我就能专注于新项目的业务逻辑, 然后再几个小时以内快速使用内置的 CI/CD 进行交付了.


About aws_ops_alpha
------------------------------------------------------------------------------
为了代码的可维护性和复用性, 我决定将所有 DevOps 相关的逻辑集成到一个 `aws_ops_alpha <https://github.com/MacHu-GWU/aws_ops_alpha-project>`_ Python 库中, 讲这些逻辑抽象成模块, 类, 方法, 以及函数. 使得我们能方便地使用 ``pip install`` 来安装然后导入这些库. 大大减少了在具体项目中的代码量.

举个例子. 对于所有的 AWS 项目, 都会涉及到多个 AWS 环境 (sandbox, test, production 等) 的部署, 这也就涉及到权限管理. 权限管理的本质是对 boto session 的管理. 而 ``aws_ops_alpha.api.AlphaBotoSesFactory`` 这个类就是专门用来管理多个环境所对应的 boto session 的. 除此之外, 所有的 AWS 项目都会涉及到 config 管理, CDK 的部署等 DevOps 逻辑. ``aws_ops_alpha`` 项目都会提供这些逻辑的抽象和封装.

这样做的好处是, 无论我选择哪种 CI 工具, 哪种 AWS Account Hierarchy, 哪种项目目录结构, 我都可以用非常少的一段代码跟已经实现好的 DevOps 逻辑相结合, 大大减少了 DevOps 的工作量. 我都可以快速的进行核心业务逻辑的开发, 而不用花费大量的时间在基础设施的搭建上.


About monorepo_aws
------------------------------------------------------------------------------
虽然 ``aws_ops_alpha`` 支持多种 CI 工具, 包括 GitHub Action 和 AWS CodeBuild 等. 在这个 ``monorepo_aws-project`` 项目中, 我们使用 GitHub Action 作为 CI 工具. 使用 monorepo 作为项目目录结构. 以后任何时候我只要做企业级的 AWS 项目, 我就只需要 clone 这个 repo, 然后用种子项目模版为新项目生成代码库, 并且一键配置好所有的基础设施. 在过去, 为了一个新项目我可能需要几天时间来搭建基础设施. 现在, 我只需要几分钟时间就可以开始写核心业务逻辑了, 并在几分钟内就能将 App 按照顺序从 sandbox, test, 一路部署到 production 中 (该工具支持任意多的 environment, 不仅仅是 sbx, tst, prd).

.. note::

    由于这个项目使用 GitHub Action 作为 CI 工具, 所以这个项目也 host 在 GitHub 上. 我在 AWS CodeCommit 上也有一个同名的姊妹项目, 它使用 AWS CodeBuild + CodePipeline 作为 CI 工具. 由于我们使用了一层抽象, 所以它们的 90% 的代码是一样的. 大大降低了我同时维护多个项目的工作量.


Seed Projects
------------------------------------------------------------------------------
在这个项目中我们提供了多种常见的种子项目. 开发者可以用这些种子项目作为模版, 替换掉里面的项目名称, AWS Account 等信息, 生成自己所需的项目代码框架. 这些种子项目包括:

- ``simple_cdk``: 创建 AWS Resources 以及 Infrastructure 的 AWS CDK 项目.
- ``simple_lambda``: 部署以 AWS Lambda Function 为核心的 Micro Services 项目. 它有三个变种, ``simple_lambda`` 使用 AWS 提供的 runtime 环境部署 Lambda Function. ``simple_lbd_container`` 使用自定义的 container image 部署 Lambda Function. 这两个变种都是用 AWS CDK 来最终部署的. ``simple_lbd_agw_chalice`` 使用 AWS Chalice 而不是 AWS CDK 来部署 Lambda Function + API Gateway.
- ``simple_glue``: 使用 AWS CDK 来部署 AWS Glue Job 来进行大数据处理
- ``simple_sfn``: 使用 AWS CDK 来部署 AWS Step Function 来进行工作流编排.


AWS DevOps Best Practice
------------------------------------------------------------------------------
上一段我们介绍了 Seed Project. 这些项目各有独特的侧重点, 但又共享许多通用的最佳实践. 例如如何管理 Git Branching, 如何管理 Dependencies, 如何管理 Configuration 等. 这些内容都在 `aws_ops_alpha 的文档 <AWS DevOps Best Practices>`_ 中有详细介绍.
