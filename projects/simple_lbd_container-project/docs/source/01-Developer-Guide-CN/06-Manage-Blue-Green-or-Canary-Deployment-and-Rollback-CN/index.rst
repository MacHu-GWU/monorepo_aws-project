Manage Blue / Green, Canary Deployment and Rollback [CN]
==============================================================================


Lambda Function Versioning and Alias
------------------------------------------------------------------------------
`Lambda function versioning and alias <https://docs.aws.amazon.com/lambda/latest/dg/configuration-aliases.html>`_ 是一个可以大大简化部署的功能. 一个 Version 是 Lambda Function 在某个时间点上的所有信息的不可变的 snapshot. 你对 Lambda Function 进行修改并不会改变这个 snapshot. 一个 alias 本质上是一个指向一个 version 的指针, 你还可以用一个 alias 指向两个 version 并且在它们之间分配流量比例. 有了这个功能, 在上一次的部署和新部署之间进行流量切换就变得非常容易了. 只要你所有的业务流量都指向 Alias 而不是 version, 那么你只要修改 Alias 指针就可以改变部署而无需真正重新运行部署, 这使得蓝绿部署就简化成了修改 Alias. 而且对于灰度部署而言, 你只要调整 Alias 所指向的两个 version 的流量比例即可. 而如果你想要进行版本回滚, 也只是修改 Alias 指针即可.

.. raw:: html
    :file: ./lambda-versioning-and-alias.drawio.html


Manage Versioning and Alias in CI/CD
------------------------------------------------------------------------------
为了更好的帮助理解在该项目中我们是如何实现 Versioned deployment 的, 我们来过一遍相关的重要文件:

1. ``config/config.json``: 该配置文件储存了非敏感的配置数据. 其中 ``"*.lambda_functions.*.live_version1": null`` 表示我们不显式指定 ``LIVE`` Alias 所指向的 version, 默认使用 ``LATEST`` version. 而 ``"*.lambda_functions.*.live_version2": null`` 和 ``"*.lambda_functions.*.live_version2_percentage": null`` 表示我们没有使用第二个 version 来进行灰度部署.

.. literalinclude:: ../../../../config/config.json
   :language: javascript
   :emphasize-lines: 18-20
   :linenos:

2. ``simple_lbd_container/iac/define/lbd.py``: 这是 CDK stack 代码定义了 ``LIVE`` alias, 并且将其指向了 ``"*.lambda_functions.*.live_version1"`` 中的值.

.. literalinclude:: ../../../../simple_lbd_container/iac/define/lbd.py
   :language: python
   :emphasize-lines: 103-140
   :linenos:

基于以上设置, 我们总是在 ``sbx`` 和 ``tst`` 环境中使用 ``LATEST`` (当然你可以通过修改配置文件指向其他的 version) 来进行开发和测试. 而每次成功的部署到 production 之后, 我们就创建一个不可变的 version, 默认指向 production 中的 ``LATEST``. 而如果我们要进行蓝绿部署, 灰度部署, 版本回滚时, 我们只要修改配置文件中的相关部分, 将 Alias 指向我们想要的版本即可.


Conclusion
------------------------------------------------------------------------------
从以上最佳实践可以看出, Version 和 Alias 是用于生产环境部署的核心技术. 它不仅仅可以应用于 Lambda, 还可以应用于任何 Application 的部署. 只不过 AWS 原生支持这种部署方式, 大大简化了我们的工作. 而对于其他的 App, 我们只要将部署抽象为一个 immutable 的 binary artifact, 使其满足 artifact 不变, 那么 app 就不变的前提, 那么对 App 的版本管理本质上就是对 artifact 的管理. 而储存带版本的 artifact 则是 AWS S3 的强项, 而储存这些 artifact 的 matadata 信息则是 AWS DynamoDB 的强项. 所以无论是什么 app, 不管官方支持还是不支持, 我们都可以以较低的成本自己实现这种最佳实践. 而 AWS Lambda 底层也正是用的 S3 + DynamoDB 来管理 version, 只不过 S3 和 DynamoDB 都是在 AWS 自己内部的 Service Account 上, 对外不可见罢了.

我个人开发了一个开源项目, 实现了对 Artifact 进行 version 和 alias 的管理, https://github.com/MacHu-GWU/versioned-project, 基于此, 我就可以让任何 App 都用上 version 和 alias 的功能了.
