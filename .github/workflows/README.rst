GitHub Action Workflows in monorepo_aws
==============================================================================
这个项目是一个用单个 Repo 来管理许多个 AWS Project 的 CI/CD 的最佳实践. 使用 GitHub Action 作为 CI/CD 的工具.


check_cross_account_permission
------------------------------------------------------------------------------
在第一次创建这个 Repo 的时候, 你需要运行 `Bootstrap <../../bootstrap>`_ 来为你所要使用的多个 AWS Account 配置好必要的资源. 其主要是各种 IAM Role 和 Cross Account Access 权限.

Bootstrap 完成后, 这个 GitHub Action Workflow 可以用来检查在 CI job run 时你的 DevOps AWS Account 是否可以 Assume Workload Account 中的 IAM Role.


dummy_lambda_app
------------------------------------------------------------------------------
在这个 Monorepo 的 CI/CD Setup 中, 大部分项目的 Workflow 都只有两个步骤:

1. Build: 在 DevOps Account 中进行 Unit Test, 构建, build artifacts.
2. Deploy: 依次进入各个 Workload Account, 用构建好的 artifacts 将 App 部署到 AWS. 并进行 Integration Test.

所以你会看到大部分的 Project 在 ``.github/workflows`` 目录下都有两个文件, 一个是 ``${name}.yml`` 是直接被 Git Push trigger 的 Workflow. 先执行 Build. 另一个是 ``${name}-deploy.yml``. 它是被 ``${name}.yml`` 所调用, 里面主要是 Deploy 的逻辑. 因为我们要在每个 Workload Account 执行类似的逻辑, 所以把这部分的逻辑抽取出来, 以便复用.

而 ``dummy_lambda_app`` 是一个极简的 Dummy Project. 它里面的 Unit Test, Build Artifact, 以及 Deploy 都仅仅是 Echo. 用来演示整个 CI/CD 的流程. 以及帮助理解 ``${name}.yml`` 和 ``${name}-deploy.yml`` 之间是如何配合工作的.

除了 ``dummy_lambda_app`` 之外, 你还能看到 ``simple_cdk1``, ``simple_cdk2``, ``simple_lambda`` 等等 这些 Project 都是用的类似的设置.


The simple_lambda Example
------------------------------------------------------------------------------
为了更好的理解我们是如何使用 GitHub Action 进行 CI/CD 的, 建议仔细阅读 `simple_lambda.yml <./simple_lambda.yml>`_ 和 `simple_lambda-deploy.yml <./simple_lambda-deploy.yml>`_ 这两个文件中的注释. ``simple_lambda`` 是一个用来展示如何部署 AWS Lambda Function 的例子. 其中包含了, 创建虚拟环境, 安装依赖, 执行单元测试, 构建 Lambda Layer 依赖, 部署 AWS CDK Stack, 执行集成测试, 并按照 sbx, tst, prd 的顺序把这一套流程再执行一遍. 其他的项目跟这个例子的流程是类似的.


simple_release
------------------------------------------------------------------------------
按照微服务架构的设计, 每个 Project 都是一个可以单独部署的微服务. 而有的时候我们需要将多个微服务一起部署. 这个 Workflow 就是用来服务这个场景的. 它的本质就是以并行或者串行的方式运行前面的 ``${name}.yml``.
