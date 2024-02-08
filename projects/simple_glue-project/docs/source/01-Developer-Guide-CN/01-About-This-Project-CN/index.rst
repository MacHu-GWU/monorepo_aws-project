About This Project [CN]
==============================================================================
这个项目是一个用来演示我于多年生产实践中总结出的一套用于生产环境中的 AWS Glue 项目的最佳实践. 里面的业务逻辑虽然非常简单, 但涵盖了生产实践中会遇到的各种挑战. 每当我做新的类似的项目时都会参考这个项目.

同时, 这个项目也是一个 "模板项目", 可以让我只用填写几个名字, 就能生成除了实际业务逻辑以外的所有代码, 使得我能专注于业务逻辑, 而能更快的让项目产生商业价值.

由于这种模板化的设计, 在企业项目管理时, 实现了 "一次设计, 处处收益". 无需所有的团队成员了解项目的所有细节, 新成员只需要能专注于业务逻辑进行开发, 就能快速的交付并产生商业价值.


What is AWS Glue Project
------------------------------------------------------------------------------
`AWS Glue <https://aws.amazon.com/glue/>`_ 是 AWS 的一个用于运行 Data ETL Batch Job 的全托管服务. 你无需管理运算环境的基础设施, 只需要专注于 Spark 业务代码, 即可运行 Data ETL 业务.

所谓 Simple Glue Project 就是一个专注于开发并快速交付 Data ETL Job 的项目. 其中包含了一整套为这个目的而设计工具链, 包括:

1. 本地开发环境.
2. 本地单元测试工具.
3. Glue Artifacts 构建工具.
4. 基础设施即代码部署工具.
5. 多环境部署工具 (sbx, tst, prd).
6. 集成测试工具
7. 在本地进行 Spark Job 的开发工具.
8. 在本地运行 Spark Job unit test 和 integration test 的开发工具.
9. 中心化的多环境配置管理工具.
10. CI 自动化构建, 测试, 部署工具.
11. 多环境 CD 自动化部署管道.
12. 生产环境中的 蓝绿部署, 以及在出现错误时版本回滚工具.

以上的所有工具链都是模块化的工具, 即可以单独拿出来在其他任何项目中使用, 而这个项目中我们已经将这些工具都整合到了一起可以无缝配合使用了.


AWS Glue Tools
------------------------------------------------------------------------------
**aws_glue_artifact**

许多 AWS 的计算服务都支持 Version 和 Alias 功能. 这两个功能使得 blue / green, canary deployment, rollback 变得异常容易. 但是 AWS Glue 不支持这两个功能. 另外 AWS Glue 的 artifacts 比较 tricky. 如果你的 Glue Job 依赖于一些你自己的代码, 那么你需要将这些代码打包成 zip 文件通过 ``--extra-py-files`` 参数传进去. 虽然 AWS CDK 以及一些其他工具提供了打包的功能, 但是和之前一样, 这些 Artifact 也没有 Version 管理. 为了解决这一问题, 我开发了 `aws_glue_artifact <https://github.com/MacHu-GWU/aws_glue_artifact-project>`_ 项目, 可以方便地构建 Glue Artifact 以及对它们进行版本管理.

**aws_glue_artifact**

由于 Glue 底层是 Spark. 在本地配置一个 Spark 的运行环境可并不容易. 所以很多开发者会使用 AWS Glue Studio 中的 Jupyter Notebook 来进行开发. 并且由于 Spark Job 的逻辑主要是 Data ETL, 做过 Spark ETL 的人都知道对其进行单元测试有多麻烦. AWS 官方提供了一个 `Glue 的 container <https://aws.amazon.com/blogs/big-data/develop-and-test-aws-glue-version-3-0-jobs-locally-using-a-docker-container/>`_, 但是要运行这个 container 的方法也不容易, 参数众多. 为了解决这一问题, 我开发了 `aws_glue_container_launcher <https://github.com/MacHu-GWU/aws_glue_container_launcher-project>`_ 项目. 这是一个能方便地在使用 Glue container 的小工具. 使得你可以在本地用 Glue Jupyter Notebook 进行交互式开发, 也可以在本地对 ETL Code 进行单元测试, 也可以在本地模拟运行一个 Glue Job. 这使得在 CI 中对 Glue Job 进行单元测试变的可能, 并且友好的本地开发环境能大大提高开发效率.


Code Architecture
------------------------------------------------------------------------------
- ``scripts``: 一些为了方便开发者使用的脚本.
- ``tests``: 非 Glue ETL 逻辑相关的单元测试.
- ``tests_glue``: Glue ETL 逻辑相关的单元测试.
- ``tests_int``: 非 Glue ETL 逻辑相关的集成测试.
- ``tests_glue_int``: Glue ETL 逻辑相关的集成测试.
- ``tests_glue_int_manual``: 需要手动执行的 Glue Job 集成测试.


Business Logic in This Project
------------------------------------------------------------------------------
这个项目主要是为了演示目的. 它包含了两种类型的 Glue Project:

1. Glue python library. 一个可以 Spark job 中被 import 的库. 它本身不是一个 ETL job, 但可以方便开发者写 ETL job.
2. Glue ETL script. 一个可以在 AWS Glue 运行的 ETL Job 的源代码.


What's Next
------------------------------------------------------------------------------
从下一篇文档开始, 我们将详细介绍如何使用这个项目模板进行新项目开发的流程. 其中包含了如何创建新项目, 以及如何以一个发布周期作为基本单位进行快速迭代.
