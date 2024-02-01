GitHub Action Workflows in monorepo_aws
==============================================================================
这个项目是一个用单个 Repo 来管理许多个 AWS Project 的 CI/CD 的最佳实践. 使用 GitHub Action 作为 CI/CD 的工具.


check_cross_account_permission
------------------------------------------------------------------------------
在第一次创建这个 Repo 的时候, 你需要运行 `Bootstrap <../../bootstrap>`_ 来为你所要使用的多个 AWS Account 配置好必要的资源. 其主要是各种 IAM Role 和 Cross Account Access 权限.

Bootstrap 完成后, 这个 GitHub Action Workflow 可以用来检查在 CI job run 时你的 DevOps AWS Account 是否可以 Assume Workload Account 中的 IAM Role.
