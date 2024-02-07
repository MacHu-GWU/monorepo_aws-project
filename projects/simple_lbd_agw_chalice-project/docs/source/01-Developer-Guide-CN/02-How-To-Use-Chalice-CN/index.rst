How To Use Chalice (CN)
==============================================================================
Chalice 框架虽然在我看来是 Python + Lambda + API Gateway 项目的最强部署工具, 没有之一. 但是由于它没有那么的流行, 并且在我们这个项目中很多使用 Chalice 的技巧在官方文档中没有体积, 所以我觉得有必要详细说说在这个项目中我们是如何使用 Chalice 的.


Dependency Layer
------------------------------------------------------------------------------
Chalice 提供了 `Automatic Lambda Layers <https://aws.github.io/chalice/topics/packaging.html#automatic-lambda-layers>`_ 的功能. Chalice 只是在运行 chalice 命令的环境中直接构建 Layer. 对于用 C 实现的 Python 库, 你构建出来的 Layer 可能在 Lambda 中不能用. 正确的做法是在本地用 Container 来构建. 或者在 CI 中用跟 Lambda Runtime 一样的环境进行构建. 所以在本项目中我们没有使用 Chalice 提供的 Automatic Lambda Layers 功能, 而是由我们自己管理.

具体做法请参考 :func:`simple_lbd_agw_chalice.ops.publish_lambda_layer` 的具体实现.


Lambda Source Code
------------------------------------------------------------------------------
根据 Chalice 官网 `App Packaging <https://aws.github.io/chalice/topics/packaging.html>`_ 一章的说明, 我们的自动化脚本 :func:`simple_lbd_agw_chalice.ops.run_chalice_deploy` 会在执行 ``chalice deploy`` 之前, 将源代码拷贝一份到 ``lambda_app/vendor/`` 目录下. 而每次部署大概率都是更新源代码, 而不是依赖. 由于源代码体积很小, 所以部署会非常快.


Chalice Configuration
------------------------------------------------------------------------------
根据 Chalice 官网 `Configuration File <https://aws.github.io/chalice/topics/configfile.html>`_ 一章的介绍, Chalice 会根据在 ``lambda_app/.chalice/config.json`` 中的定义来部署 Lambda Function 和 API Gateway. 但是我们的项目已经有一套更佳完善的 Configuration 管理系统了, 我们没必要在这套系统和 Chalice 的 Configuration 系统中维护两套一模一样的配置. 这样不利于代码维护, 且容易忘记让两套系统保持一致. 所以在本项目中, 我们使用 ``lambda_app/update_chalice_config.py`` 脚本来自动将我们的配置同步到 Chalice 的配置文件中. 每次执行 ``chalice deploy`` 之前, 我们都会先执行这个脚本.


Chalice Deployed JSON
------------------------------------------------------------------------------
每次成功运行 ``chalice deploy`` 之后, 它都会把已经部署的 Resource 记录在 ``lambda_app/.chalice/deployed/${env_name}.json`` 文件中. 官方推荐我们将这个文件加入到版本控制中. 由于我们的部署发生在 CI/CD 环境中, 这个文件会在 CI 环境中更新. 而我们是不宜在 CI 环境中自动执行 Git Commit 的. 所以我们选择用 AWS S3 来作为这个 deployed JSON 文件 (每个环境一个) 的存储. 我们在 S3 中有一个目录 (请参考 ``config.s3dir_deployed`` 变量的定义) 专门用于储存所有的 deployed JSON 文件以及它们的所有历史版本. 每次执行 ``chalice deploy`` 之前, 我们会从这个目录下载对应的 deployed JSON 文件, 然后成功执行完 ``chalice deploy`` 之后会将本地的 deployed JSON 文件上传到 S3. 这一套逻辑是在 :func:`simple_lbd_agw_chalice.ops.run_chalice_deploy` 中实现的.

值得注意的是, 我们的实现还包含了一个分布式锁机制, 确保同一时间只有一个程序正在运行 chalice deploy 并对 deployed JSON 文件进行更新.
