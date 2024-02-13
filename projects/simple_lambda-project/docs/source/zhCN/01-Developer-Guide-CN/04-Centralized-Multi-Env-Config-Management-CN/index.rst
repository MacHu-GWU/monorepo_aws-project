Centralized Multi Environment Config Management (CN)
==============================================================================
本项目使用了 ``aws_ops_alpha`` 所推荐的 `Centralized Multi Environment Config Management <https://aws-ops-alpha.readthedocs.io/en/latest/zhCN/01-AWS-DevOps-Best-Practices-CN/10-Centralized-Multi-Env-Config-Management-CN/index.html>`_ 最佳实践.


Config Management Related Modules
------------------------------------------------------------------------------
下面我们列出了所有跟 Config Management 有关的模块::

    simple_lambda/config # the root folder of the config management system source code
    simple_lambda/config/define # config schema definition
    simple_lambda/config/define/main.py # centralized config object, config fields are break down into sub-modules
    simple_lambda/config/define/app.py # app related configs, e.g. app name, app artifacts S3 bucket
    simple_lambda/config/define/lbd_deploy.py # Lambda function deployment related configs
    simple_lambda/config/define/lbd_func.py # per Lambda function name, memory size, timeout configs
    simple_lambda/config/load.py # config value initialization
    config/config.json # include the non-sensitive config data
    ${HOME}/.projects/simple_lambda/config-secret.json # include the sensitive config data, the ${HOME} is your user home directory
    tests/config/test_config_init.py # the unit test for config management, everytime you changed any of the config.json, or config/ modules, you should run this test


Config Schema Declaration
------------------------------------------------------------------------------
``simple_lambda/config/define/`` 模块定义了 Config Schema. 我们将众多的 Config value 分为两类:

1. static value: 需要从 backend data store 读取的静态数据. 这些数据一般都是 scalar value. 通常被定义为一个 attribute.
2. derived value: 通常是根据 static value 以及其他因素计算得来的值. 通常被定义为一个 method.

我们按照业务将 Config field 分散到不同的模块中.


Config Loading
------------------------------------------------------------------------------
``simple_lambda/config/load.py`` 模块负责实例化 Config 对象.


Update Config Module Workflow
------------------------------------------------------------------------------
如果你需要对 Config 的 Declaration, 或是 config.json 中的值进行修改, 推荐你按照下列顺序进行操作:

1. 如果你要修改 Config Declaration 的定义, 在 ``simple_lambda/config/define/`` 模块中进行修改.
2. 如果你要修改 Config 的值, 在本地电脑上修改 ``config/config.json`` 和 ``${HOME}/.projects/simple_lambda/config-secret.json`` 文件.
3. 更新 ``tests/config/test_config_load.py`` 单元测试, 确保能反映出你对 Config Declaration 的修改. 如果你没有改变 Declaration, 大概率你不需要修改这个文件.
4. 运行 ``tests/config/test_config_load.py`` 单元测试, 确保你的修改没有引入错误.
6. 运行 ``make deploy-config`` 将 config 的修改部署到 AWS Parameter Store. 如果你想反悔, 只要在 Git 中撤销你的修改, 再重新运行一次这条命令即可. 你永远可以在 AWS Parameter Store 中的历史版本中看到 Config 曾经的值.
7. 如有必要, 在本地运行 ``make deploy-app`` 来尝试部署 App 到 sandbox. 然后运行 ``make int`` 使用部署的资源进行集成测试. 这个过程中会使用到 config.
