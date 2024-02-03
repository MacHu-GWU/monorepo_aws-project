About ``bootstrap`` Folder
==============================================================================
在 "single repo" (单个 Git 仓库), "multi deployment units" (多个可独立部署的单元) 的架构下, 每个 deployment unit (后面简称 DU) 都有它们专属的 `CodeBuild project <https://docs.aws.amazon.com/codebuild/latest/userguide/working-with-build-projects.html>`_ 来运行 CI (Continue Integration, 持续集成) 逻辑, 以及专属的 `CodePipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html>`_ 来运行 CD (Continue Deployment, 持续部署) logic. 所以, 在开始开发一个新的 DU 之前, 都需要用 bootstrap 来创建这些用于 CI/CD  的资源.

相比这种设计, 还有一种设计就是为所有的 DU 配置一套共享的 CI/CD 资源. 在生产中我们两种设计都使用过很长时间, 根据我们的实践经验, 我们最终选择了为每个 DU 配一套专属的 CI/CD 资源. 因为其实每个 DU 的特点都不一样, 很难用一套方案来解决所有的问题. 在我们的设计中, 所有的 CI/CD 资源都是 serverless 并且是 stateless 的, 非常轻量, 可以随时创建和删除而不会影响已经部署的 DU, 那么就配置一套共享资源来提高资源利用率的优势就不存在了. 另外一个原因是, 如果我们使用一套共享资源, 那么很难对每个 DU 进行拆分和自定义. 而如果我们为每个 DU 配一套专属资源, 我们将多个 DU 组合起来用一个脚本管理却非常的方便, 大大的提高了灵活性.


CI/CD Resources for each Deployment Unit
------------------------------------------------------------------------------
下面介绍了每个 DU 所需的 CI/CD 资源列表:

- 一个 AWS `Lambda Function <https://docs.aws.amazon.com/lambda/latest/dg/welcome.html>`_ 用于处理 CodeCommit event, 对其进行分析并决定是否要运行 CodeBuild CI Job Run, 以及运行哪个 CodeBuild Project.
- 一个给 Lambda Function 的 `IAM Role <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html>`_.
- 一个 AWS `Event Rule <https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rules.html>`_ 用于捕获 CodeCommit reference create / update (create, update branch, push commits) events, 并根据 branch 的名称对其进行过滤, 然后 trigger 前面的 Lambda Function.
- 一个 AWS `CodeBuild Project <https://docs.aws.amazon.com/codebuild/latest/userguide/working-with-build-projects.html>`_ 用来执行持续集成逻辑.
- 一个给 CodeBild Project 的 IAM Role.
- 一个 AWS `CodePipeline <https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html>`_ 用来执行持续交付逻辑.
- 一个给 CodePipeline 的 IAM Role.

对于我们这个 AWS Batch 项目, 还需要额外的 CI/CD 资源:

- 一个给 AWS CodeBuild 中所运行的 container 用的 IAM Role. 这是因为在 CodeBuild 中运行的 container 是一个隔离的沙箱环境, 并不能自动继承 CodeBuild 中的 IAM 权限. 根据官方博客的说明, 正确的做法是用 CodeBuild 的 Role assume 一个 Role (就是这个 Role), 并将 assumed role 的 credentials 用 environment variables 的方式通过 ``docker build`` 命令 pass 到 container runtime 中.


Files in this Folder Walkthrough
------------------------------------------------------------------------------
让我们来快速过一遍这个目录下的所有文件.


Deployment Unit Config ``du-config.json``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
这个文件是 Deployment Unit 的 CI/CD 相关的配置.

- du_name: 是这个 DU 的名字, 有这个 prefix 的 git branch 才会触发对应的 CI/CD
- du_folder: 这个 DU 项目的根目录, 我们需要通过这个目录定位到 buildspec.yml 文件
- du_name_prefix: 所有属于这个 DU 的 CI/CD resource 名字的前缀, 这个前缀的完整版是 ``${repo_name_prefix}-${du_name_prefix}``, 其中 ``${repo_name_prefix}`` 是这个 Git repo 相关的资源的名字的前缀.

.. code-block:: javascript

    {
        // deployment unit name, this is the git branch prefix that triggers the CI/CD
        "du_name": "simple_lbd_container",
        // this is the sub-folder name of your deployment unit, the relative path to
        // git repo root dir should be "projects/${du_folder}/"
        // it has to have a buildspec.yml file in it.
        "du_folder": "simple_lbd_container-project",
        // this is the common prefix for all the AWS resource name for this deployment unit
        // the full prefix is actually "${repo_name_prefix}-${du_name_prefix}"
        // where the ${repo_name_prefix} is defined in the "shared/repo-config.json" file
        "du_name_prefix": "simple_lbd_container"
    }


``app.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
这是 bootstrap 的 CDK 代码. 它定义了所有需要的 CI/CD Resources.


``bootstrap_cli.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
这是一个用来进行 bootstrap (创建资源) 或是 teardown (删除资源) 的 CLI 工具. 它是对 ``cdk`` 命令行的封装. 但是它是需要一些 Python 依赖, 并需要在 virtualenv 中运行的. 不要担心, 我们还有一个脚本对 ``bootstrap_cli.py`` 又进行了封装, 自动化了创建 virtualenv 和安装依赖的过程, 实现了零依赖直接安装.

除非你非常了解这个工具的原理, 不然不推荐直接使用它.


``bootstrap_lib.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
它是对 ``bootstrap_cli.py`` 的二次封装, 自动化了创建 virtualenv 和安装依赖的过程, 实现了零依赖直接安装.

除非你非常了解这个工具的原理, 不然不推荐直接使用它.


``bootstrap.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
进行 bootstrap 的自动化脚本, 直接用 Python3.7+ 运行它即可::

    python bootstrap.py


``teardown.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
进行 teardown 的自动化脚本, 直接用 Python3.7+ 运行它即可::

    python teardown.py


``codebuild_trigger_lambda/lambda_function.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
这个是用来处理 CodeCommit Events 并 trigger CodeBuild project 的 Lambda Function 源码. 请阅读源码了解默认的规则. 当然你也可以用简单的 ``if ... else ...`` 对它进行自定义. 简单来说就是:

- ``main``, ``release``, ``chore`` branch: 什么都不做
- Commit message 中带 ``chore``: 什么都不做
- 如果 branch 名带有 ``${du_name}/...`` 前缀, 则触发对应的 CodeBuild project


``build_lambda_source.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
这个是用来创建 Lambda Function 的 deployment package 的自动化脚本. 该脚本会在 ``app.py`` 中被执行.


``requirements.txt``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
bootstrap 所需的 Python 依赖. 你无需手动安装他们, 我们的 ``bootstrap.py``, ``teardown.py`` 自动化脚本会自动安装它们. 如果你想要手动来运行 ``bootstrap_cli.py``, 你可以自己创建 virtualenv 并安装它们.


Run Bootstrap
------------------------------------------------------------------------------
每当你创建了一个新的 Deployment Unit Project, 你需要创建 CI/CD 所需的 AWS Resources::

    cd projects/${du_folder}/bootstrap
    python bootstrap.py

如果你想删除这些 CI/CD 的 AWS Resources 你可以这么做::

    cd projects/${du_folder}/bootstrap
    python teardown.py


Next Step
------------------------------------------------------------------------------
至此你已经成功地为你的 Deployment Unit 项目创建了所需的 CI/CD 资源了. 你可以开始进行项目开发了. 在开始写 Code 之前, 推荐你阅读 ``${du_folder}/README.rst`` 中的开发者指南, 学习如何进行该项目的开发.
