About This Project (CN)
==============================================================================
在我的工作中经常要交付各种各样的 AWS 项目, 包括 Infrastructure as Code 项目, AWS Lambda 项目,  API Gateway 项目, AWS Batch 项目, AWS Step Function 项目, AWS ECS Task 项目, AWS Glue ETL 项目, AWS SageMaker ML 项目. 有时这些项目一个个彼此独立. 有的时候这些项目虽然是被独立部署和维护, 但是互相之间有着非常紧密的联系.

在工作中, 我往往要为每一个新的项目创建一个 Git repo, 并且创建 CI/CD 的资源, 搭建基础设施. 但是对于不同的项目往往会选择不同的 CI 工具, 不同的 AWS Account Hierarchy, 不同的项目目录结构. 虽然有着很多的历史经验可以参考, 但是每次做新项目依然有很多前期工作要做.

于是, 我决定将这些项目经验集成到一个 `aws_ops_alpha <https://github.com/MacHu-GWU/aws_ops_alpha-project>`_ Python 库中, 将这些不同的选择进行抽象化, 使得无论我选择哪种 CI 工具, 那种 AWS Account Hierarchy, 那种项目目录结构, 我都可以快速的进行核心业务逻辑的开发, 而不用花费大量的时间在基础设施的搭建上.

``aws_ops_alpha`` 支持多种 CI 工具, 包括 GitHub Action 和 AWS CodeBuild 等. 在这个 ``monorepo_aws-project`` 项目中, 我们使用 GitHub Action 作为 CI 工具. 使用 monorepo 作为项目目录结构. 以后任何时候我只要做企业级的 AWS 项目, 我就只需要 clone 这个 repo, 然后用种子项目模版为新项目生成代码库, 并且一键配置好所有的基础设施. 在过去, 为了一个新项目我可能需要几天时间来搭建基础设施. 现在, 我只需要几分钟时间就可以开始写核心业务逻辑了, 并在几分钟内就能将 App 按照顺序从 sandbox, test, 一路部署到 production 中 (该工具支持任意多的 environment, 不仅仅是 sbx, tst, prd).

.. note::

    由于这个项目使用 GitHub Action 作为 CI 工具, 所以这个项目也 host 在 GitHub 上. 我在 AWS CodeCommit 上也有一个姊妹项目, 它使用 AWS CodeBuild + CodePipeline 作为 CI 工具. 由于我们使用了一层抽象, 所以它们的 90% 的代码是一样的. 大大降低了我同时维护多个项目的工作量.
