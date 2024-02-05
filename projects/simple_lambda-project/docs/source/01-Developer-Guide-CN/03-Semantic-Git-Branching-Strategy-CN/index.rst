Semantic Git Branching Strategy [CN]
==============================================================================
由于 CI 系统的编排定义语言通常不是完备的编程语言, 一个常见的缺陷是无法用自定义的 ``if ... else ...`` 逻辑来选择是否执行 CI 编排中的某一个步骤. 例如, Build AWS Lambda Layer 非常耗时, 而且不需要那么频繁的更新, 所以我们只想要在某个特定的 branch 上做这件事. 又例如我们仅仅是进行了一个小的 feature improvement, 我们没有进行任何的部署, 自然也不需要运行 integration test. 这些逻辑在 CI 系统的编排定义语言中很难实现, 也不好维护.

虽然现代的 CI 系统例如 GitHub Action, 都会提供一些语法来进行简单的 IF Else 判断. 但是这只适合只有 branch name 一个维度的情况. 在实际企业项目中, 往往是由 branch, environment name (sbx, test, prd), runtime (local or CI) 等多个维度共同决定的. 这个时候就不是用简单的 if else 能够解决的了.

在有多个维度同时参与条件判断时, 最佳做法是用 truth table, 把所有的条件的排列组合枚举出来并定义返回的 boolean 值. 这个真值表的功能在本项目中由 `tt4human <https://github.com/MacHu-GWU/tt4human-project>`_ 提供. 而具体如何将真值表功能整合到 CI 系统中则由 `aws_ops_alpha <https://github.com/MacHu-GWU/aws_ops_alpha-project>`_ 库提供. 详细的设计文档请参考 `Rule Set <https://aws-ops-alpha.readthedocs.io/en/latest/01-AWS-DevOps-Best-Practices/04-Rule-Set-CN/index.html>`_.
