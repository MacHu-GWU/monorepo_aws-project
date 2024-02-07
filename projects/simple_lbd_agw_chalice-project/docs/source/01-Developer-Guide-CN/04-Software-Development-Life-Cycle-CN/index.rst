Software Development Life Cycle (SDLC) [CN]
==============================================================================
本文档将介绍我们如何使用这个项目模板进行新项目开发的流程. 其中包含了如何创建新项目, 以及如何以一个发布周期作为基本单位进行快速迭代.


0. Short Version
------------------------------------------------------------------------------
本节适用于你已经通读了全部文档, 但需要随时回来查阅的情况. 如果你是第一次阅读本文档, 可以跳过此节.

**BootStrap**

1. CD to the cookiecutter directory::

    cd ./cookiecutter

2. BootStrap::

    python new_project_like_simple_lbd_agw_chalice.py

3. Copy the generated project skeleton from ``./cookiecutter/tmp/template-project/${your_project_name}`` directory to the ``./projects/${your_project_name}`` directory.

**SDLC**

1. 在 ``simple_lbd_agw_chalice/feature`` branch 开发. 进行 config management, 核心业务逻辑相关的代码开发以及完成单元测试. 然后就可以 PR + Merge 了.
2. 在 ``simple_lbd_agw_chalice/layer`` branch 开发, 更新依赖. 在这一步请不要修改任何业务逻辑, 仅仅是更新依赖后再运行一次单元测试, 确保测试和依赖版本都兼容. 然后 push 到 Git 触发 CI job run 来构建 Lambda Layer. 确保 Layer 被成功创建后就可以 PR + Merge 了.
3. 在 ``simple_lbd_agw_chalice/app`` branch 开发核心业务逻辑, CDK stack 部署代码, 以及集成测试代码. 然后 push 到 Git 触发 CI 自动化运行单元测试, CDK stack 部署, 以及集成测试. 全部成功后就可以 PR + Merge 了
4. 创建 ``simple_lbd_agw_chalice/release`` branch 进行部署. 在这一步请不要修改任何业务逻辑, 仅仅是对配置文件进行小修小补即可. 触发 CodePipeline 一路按照 sbx, tst, prd 的顺序部署. 如果因为业务逻辑导致了部署失败, 请回滚到上一步, 更新业务逻辑和测试后再回到这一步.

至此我们的开发周期就结束了. 重复这个周期可以不断的迭代. 如果你需要清除所有的 workload environment 中的 App, 你可以创建 ``simple_lbd_agw_chalice/cleanup`` branch trigger CI job 删除所有环境中已部署的 App.


1. Bootstrap - Create a New Project Code Skeleton
------------------------------------------------------------------------------
本节介绍了如何用这个 ``simple_lbd_agw_chalice-project`` 作为种子模板, 为新项目快速生成除了业务逻辑以外的全部代码. 使得你可以专注于业务逻辑的开发, 而无需手动将 DevOps 脚本 wire 到 CI/CD 系统中.

首先, 确保你位于 ``cookiecutter`` 目录下. 然后运行下面的命令来创建新项目. 它会问你一些关于你的新项目名字, 你打算用哪个 AWS Account 来部署之类的问题, 让你填写一些文本, 然后就会自动生成新项目了. 如果你想了解这个功能是如何实现的, 请查看 ``cookiecutter/README.rst``:

    python new_project_like_simple_lbd_agw_chalice.py

然后将刚刚生成的 ``cookiecutter/tmp/template-project/${your_project_name}`` 目录, 也就是你的新项目的代码目录, 复制到 ``./projects/${your_project_name}`` 下. 按照我们的项目文件结构设计, 每一个可以单独部署的新项目都需要位于 ``./projects/`` 目录下. 其中 ``${your_project_name}`` 就是你生成新项目时填写的项目名, 这里为了解说方便, 我们就假设你的项目名称还是 ``simple_lbd_agw_chalice-project`` 好了. 从现在起, 我们每当说到 ``simple_lbd_agw_chalice-project``, 就指的是 ``./projects/simple_lbd_agw_chalice-project/`` 这个目录. 虽然它和模板项目名字一摸一样, 但是模板项目本身也是一个完全可以一行代码不改就能运行, 测试, 部署的项目, 所以性质上是一样的. 这里要说明一下 ``simple_lbd_agw_chalice-project`` 是你的项目的文件夹名, 而 ``simple_lbd_agw_chalice`` 则是 **Deployment Unit Name**, 也就是 ``${du_name}``. 项目的 Python 包也会叫这个名字, 并且所有的 AWS Resource Name 都会包含这个 ``${du_name}`` 前缀. 所以每当我们说到 ``simple_lbd_agw_chalice``, ``${du_name}``, 我们指的是同一个东西.

由于你刚刚生成了新项目, 从现在开始我们的所有操作就要在 ``./projects/simple_lbd_agw_chalice-project/`` 这个目录下进行了.


2. SDLC - A Full Release Cycle
------------------------------------------------------------------------------
本节以一个发布周期为例, 介绍了在一个发布周期内如何进行开发, 测试, 部署的具体步骤. 一个成熟的业务很少能一蹴而就, 都是经过反复迭代打磨之后形成的. 所以如果我们能掌握快速开发迭代的最佳实践, 就能让代码更快地创造商业价值.

注: 本项目的所有自动化脚本都基于 MacOS / Linux 系统. 如果你用的是 Windows, 建议迁徙到 MacOS 或是使用 WSL (Windows Subsystem for Linux). 因为开发环境和生产环境保持一致对于软件开发能避免很多没有必要且没有价值去解决它的麻烦. 所以还是建议不要用 Windows 作为你的主力开发环境.


2.1 SDLC - Feature Development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
一个发布周期的第一步就是开发新功能.

1. 创建一个 ``simple_lbd_agw_chalice/feature/${description}`` 的 branch, 它的命名规则是 ``${du_name}/feature/${description}``.
2. 这个项目的所有 SDLC 自动化脚本都是用 Python 实现的, 并且有一些依赖. 你需要在你的全局 Python, 通常是用 `pyenv <https://github.com/pyenv/pyenv>`_ 安装的 Python (注意, 不是你的系统 Python) 运行下面的命令来安装依赖::

    pip install -r requirements-automation.txt

3. 为 ``simple_lbd_agw_chalice`` 项目创建 virtualenv 虚拟环境. 该项目的自动化脚本都用 ``make`` 封装好了. 你可以直接输入下面的命令来创建虚拟环境. 其中虚拟环境会被创建在 ``simple_lbd_agw_chalice-project/.venv/`` 目录下::

    make venv-create

4. 在你安装任何项目依赖之前, 你需要 resolve 所有的依赖的具体版本来确保你的依赖是 deterministic 的 (如果你刚从 Seed 生成项目模版, 并不打算添加任何新的依赖, 那你可以跳过 resolve 这一步, 因为你的项目的依赖跟 seed project 一模一样, 无需进行更改). deterministic 的含义是, 如果你的代码没有变, 那么你的依赖无论在哪台机器上安装, 何时安装, 最终的结果是一摸一样的, 一个比特都不会错. 这样才能保证你的部署能长时间保持一致. 不然你今天的部署和明天的部署生成的依赖不一样, 那么你随时都需要解决因为依赖导致的奇怪问题, 而这些工作是毫无价值的. 该项目使用了 `poetry <https://python-poetry.org/>`_ 来实现 deterministic dependencies, 你可以运行下面的命令来 resolve 依赖::

    make poetry-lock

5. 现在你可以根据 resolve 的结果来安装依赖了. 我们的依赖按照功能被分为了 5 组. 第一组是运行核心业务逻辑的核心依赖. 第二组是在开发时能帮助我们提高效率的 dev 依赖. 第三组是生成项目文档网站的 doc 依赖. 第四组是运行测试的 test 依赖. 第五组是运行 SDLC 自动化脚本的 automation 依赖. 你可以用 ``make install-all`` 命令安装所有依赖. 也可以用 ``make install``, ``make install-dev``, ``make install-doc``, ``make install-test`` and ``make install-automation`` 命令分别安装指定的依赖::

    make install-all

6. 进入虚拟环境, 这没什么好说的::

    source .venv/bin/activate

7. 现在你可以在本地运行代码覆盖率测试 (coverage test, 单元测试的一种). 如果你是第一次学习这个项目模板, 建议你不要修改任何业务逻辑代码. 模板生成的代码本身就是一个完整的可部署的项目, 并且单元测试都是通过的. 代码覆盖率测试能显示哪些代码没有被测试所覆盖, 也就意味着在生产环境中可能会出现不可预料的风险. 我建议一个生产项目至少保持 90% 以上的测试覆盖率. 你可以用下面的命令来运行代码覆盖率测试. 你也可以用 ``make view-cov`` 命令在浏览器中查看哪些代码没有被测试所覆盖::

    make cov

8. 该项目有一个 config management 系统. 在本地测试时我们使用的是位于本地电脑上的配置文件. 由于你不能将敏感数据, 例如数据库密码, 这一类的信息 check in 到 Git, 所以在CI/CD 中运行测试时, 这些配置文件不存在. 我们需要将本地的配置文件部署到专用的配置数据管理服务 `AWS SSM Parameter Store <https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html>`_ 中. 你可以运行下面的命令部署配置文件::

    make deploy-config

9. 至此, 基本的功能也已经实现, 也进行了测试, 你的本地开发工作已经做完了. 你可以将你的 branch push 到 Git, 然后开始一个 pull request, 并邀请其他开发者进行 code review. feature branch 会自动 trigger 一个 CodeBuild job run 来运行单元测试. 你可以用下面的命令来显示该项目的一些重要信息. 例如一些重要的文件和目录的路径, 项目用来做 CI/CD 所使用的 CodeBuild Project 和 CodePipeline 的 AWS Console 连接. 其中你可以点击 ``codebuild`` 连接来预览你的 CI job run 的状态和日志.

    make info

10. 如果你的 CI job run 和 code review 都通过了, 那么你就可以将 ``simple_lbd_agw_chalice/feature/${description}`` branch merge 到 ``main`` 了.

至此, 你的新功能已算是开发完毕.


2.2. SDLC - Publish Expensive Artifacts (layer, container image, etc)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
在这一步我们将要构建比较耗时的 Artifacts. 如果你用的是 AWS 托管的 container, 那么你只需要构建 Layer 即可. 而如果你的 Layer 超过了 250MB 的限制, 那么你就需要构建 custom container image. 我们这里用 Layer 为例来说明, 构建 container image 的步骤和 Layer 类似.

由于依赖并不会被频繁地更新, 所以我们仅仅会在这一步构建依赖, 而不是在整个 SDLC 周期内不断地重复构建依赖.

1. 创建一个 layer branch ``simple_lbd_agw_chalice/layer/${description}`` (``${du_name}/layer/${description}``).
2. 不要修改任何业务逻辑代码, 专注于在 ``pyproject.toml`` 中定义的依赖, 然后用 ``make poetry-lock`` 命令来 resolve 所有依赖的具体版本, 从而实现 deterministic dependency. 最后运行一次 ``make cov`` 命令确保单元测试和依赖兼容.
3. 你可以将你的 branch push 到 Git 了, 然后开始一个 pull request 并邀请其他开发者进行 code review. layer branch 会自动 trigger 一个 Codebuild job run 来运行单元测试并构建 Layer 然后自动发布一个新的 Layer 版本. 在此项目中我们还会将新的 dependencies 和 latest 的 layer 比较, 如果两者相同则跳过构建步骤以节省时间.
4. 最终当 CI 发布了一个新的 Layer version 后, 你可以将 ``simple_lbd_agw_chalice/layer/${description}`` branch merge 到 ``main`` 了.


2.3 Application logic Unit test, App Deployment and Integration test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
在这一步我们专注与业务逻辑的进一步打磨, 以及 Lambda App 的部署, 以及集成测试, 我们的目标是将 App 部署到 ``sandbox`` 环境并确保集成测试能够通过.

1. Create a lambda branch ``simple_lbd_agw_chalice/app/${description}`` (``${du_name}/app/${description}``).
2. Implement the CDK code in the ``simple_lbd_agw_chalice/iac/`` python module (The code skeleton generated from sample project should be working as it is).
3. Deploy the CDK stack via ``cdk deploy`` command. The following command is a wrapper that will handle a lot of details::

    make deploy-stack

4. Deploy the Lambda and API Gateway via ``chalice deploy`` command. The following command is a wrapper that will handle a lot of details::

    make chalice-deploy

5. Implement the integration test code in the ``tests_int/`` folder. And use real AWS Lambda and for testing.

    make int

6. Once the integration test passed on local laptop, you can publish your branch to Git, start a merge request, and invite other developer for code review. The lambda branch will automatically trigger a Codebuild to run the unit test, deploy the app to ``sandbox`` environment and run integration test.

7. Once you see the app is deployed to ``sandbox`` and the integration test is passed, you can merge the ``simple_lbd_agw_chalice/app/${description}`` to ``main``.


2.4 SDLC - Release from sandbox to test and then to production
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
至此, 你的镜像和 Infrastructure as Code 都已经部署到了 ``sandbox`` 环境并经过了充分测试了. 现在你可以将其通过 CD 管道发布到 ``production`` 了.

1. 创建一个 ``simple_lbd_agw_chalice/release`` 的 branch, 它的命名规则是 ``${du_name}/release``, 注意这里没有可选的 ``${description}`` 了. 在这个 branch 上请不要进行业务逻辑代码的改动. 这个 branch 是专门用来部署到 upper Environment 的 (所有高于 sandbox 的都是 upper Environment).
2. 这个 branch 会 trigger GitHub Action Workflow, 它会一步步的将所有的东西从 ``sbx`` 部署到 ``tst`` 然后要你 manual approve, 你 approve 通过之后就会继续部署到 ``prd`` 了.

这个 CI/CD 系统的设计我们这里不展开说, 我们只需要知道如何使用即可. 如有需要了解 CI/CD 系统的详情, 请参考 ``.github/workflows/README.rst``.


2.5 (Optional) Clean Up App Deployment and Infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
如果因为各种原因, 例如项目结束了, 需要清理掉 (删除) 所有已经部署的 AWS Resources, 该项目提供了一种便捷而安全的方式来自动删除指定的或所有的资源.

1. 创建一个 ``simple_lbd_agw_chalice/cleanup`` 的 branch, 它的命名规则是 ``${du_name}/cleanup``. 在这个 branch 上请不要进行业务逻辑代码的改动. 这个 branch 是专门用来 cleanup 的.
2. 更改 ``chore.txt`` 的内容, 然后输入如下 Commit Message. 这个 Commit Message 必须要符合 ``cleanup: ${env_name1}, ${env_name2}, ...`` 命名规则, 它会告诉 CI Job run 要 clean up 哪些环境中的资源. 如果你的 Commit Message 不是符合命名规则, 那么 CI Job run 就什么都不会做. 这种设计是为了确保开发者完全清楚自己的行为会导致什么结果, 并且用 Git commit message 在系统中留下记录.

    cleanup: sbx, tst, prd

如果你还需要将在 bootstrap 阶段创建的用于 CI/CD 的 AWS Resources 也清理掉. 你可以

2. **Clean up CI/CD resource**

- Just go to AWS CloudFormation console and delete the ``multi-env-simple-apigateway-stack`` (``${repo_name_prefix}-${du_name}-stack``) stack.
