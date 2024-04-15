Deterministic Dependency Management (CN)
==============================================================================
本项目使用了 ``aws_ops_alpha`` 所推荐的 `Deterministic Dependency Management <https://aws-ops-alpha.readthedocs.io/en/latest/zhCN/01-AWS-DevOps-Best-Practices-CN/09-Determinative-Dependency-Management-CN/index.html>`_ 最佳实践.


Dependency Management Workflow
------------------------------------------------------------------------------
如果你需要对 CDK 模块进行修改, 推荐你按照下列顺序进行操作:

1. 修改 ``pyproject.toml`` 文件中的依赖.
2. 运行 ``poetry lock`` 或 ``make poetry-lock`` 命令来解析并锁定依赖. 该操作会更新 ``poetry.lock`` 文件.
3. 在本地运行 ``make install-all`` 命令来安装你所修改的依赖.
4. 运行 ``make cov`` 命令来确保你的修改没有破坏现有的测试用例.

然后你就可以将 ``poetry.lock`` 文件以及所有自动生成的 ``requirements-xyz.txt`` 文件 commit 到 Git 中了. 如果在后续的部署阶段出现了任何问题, 而你无法修复, 你可以回滚 git commit 回到之前的依赖定义.


Related Dependency Management DevOps Commands
------------------------------------------------------------------------------
下面列出了所有跟依赖管理相关的命令. 对于本地开发来说, 最常用的命令是  ``make poetry-lock`` and ``make install-all``::

    install                                  ** Install main dependencies and Package itself
    install-dev                              Install Development Dependencies
    install-test                             Install Test Dependencies
    install-doc                              Install Document Dependencies
    install-automation                       Install Automation Dependencies
    install-all                              Install All Dependencies
    poetry-export                            Export requirements-*.txt from poetry.lock file
    poetry-lock                              Resolve dependencies using poetry, update poetry.lock file
