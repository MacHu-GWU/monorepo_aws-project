CDK Development Best Practice [CN]
==============================================================================


Code Structure Overview
------------------------------------------------------------------------------
::

    ${python_lib_name}/iac/ # the root folder of the CDK code
    ${python_lib_name}/iac/define/ # CDK stack declaration code
    ${python_lib_name}/iac/define/main.py # the main entry of the CDK code, resources are broken down into modules
    ${python_lib_name}/iac/define/iam.py # IAM resources
    ${python_lib_name}/iac/define/lbd.py # Lambda resources
    ${python_lib_name}/iac/exports.py # CDK stack output exports


CDK Stack Declaration
------------------------------------------------------------------------------
所有的 CDK Stack 的声明代码都放在了 ``${python_lib_name}/iac/define/`` 目录下. 其中 ``main.py`` 是 entry point, 也是 deployment 的入口. 而所有的资源按照逻辑


CDK Stack Output Exports
------------------------------------------------------------------------------
在微服务架构的最佳实践中, 我们尽可能的将大型系统分拆成较小的 App. 那么 App 之间互相获得对方的 metadata 必须要解决的问题. 例如一个 App 里有一些服务, 但是其他的 App 如何知道这个服务的 endpoint url 是什么呢?

`AWS CloudFormation Output Exports <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html>`_ 是 AWS 原生的一个 feature, 能将 Infrastructure as code 的 value export 给任何需要的人. 所以在本项目中, 我们使用 CloudFormation Output Exports 作为 App 之间互相拉取 metadata 的机制.

在本项目中, 除了 IAC 的 declaration code, 还有一个专门的 ``exports.py`` 模块. 它是一个零依赖即可 import 的模块, 可以直接被复制粘贴到其他项目中使用, 并提供了一套简单的 API 来获得属于本项目的 CloudFormation Output Exports. 这个模块应由本项目的开发者负责维护, 而不是让使用者自己开发一套代码. 在企业项目实践中, 经常会出现 A 找 B 要 Output Exports value, 然后 B 给 A 解释应该怎么怎么做, 然后让 A 自己写代码实现, 这是一个非常坏的模式. 首先, 这个 CDK Stack 是 B 的项目, 也是 B 来维护的, B 最清楚该怎么做. 另外 B 可能会随时修改这个 Stack 的代码, 那么 A 是不可能立刻知道 B 做了哪些改动, 应该配合做哪些修改. 最后如果有很多人都需要依赖 B 的 Output Exports value, 那么维护这些 output 的稳定性就是一个必须要解决的问题, 并且一个个的去教其他人怎么用也是一个很麻烦的工作. 而如果 B 自己维护一个模块, 同时保证这个模块的 API 稳定, 其他人只需要复制粘贴并且 import 即可. 这样减少了沟通成本, 增加了系统稳定性, 同时出了任何问题责任的边界也很清楚.

.. literalinclude:: ../../../../simple_lbd_container/iac/exports.py
   :language: python
   :linenos:
