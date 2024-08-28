ECR Container
==============================================================================


Create ECR Repository
------------------------------------------------------------------------------
在这个项目中 ECR Repository 是由 Admin 手动创建的. 我们之所以不用 CDK 来管理 ECR Repository 是因为这跟 Config 类似, 是一个全局资源, 并且里面保存的是重要 Artifacts. 我们不希望对 CDK 的误操作导致 ECR Repository 被删除. 所以我们选择手动创建.


你可以执行 ``make create-ecr-repository`` 命令来在 DevOps AWS Account 中创建一个 ECR Repository. 这个 make 命令会调用下面的 Python 脚本.

.. dropdown:: bin/s04_08_create_ecr_repository.py

    .. literalinclude:: ../../../../bin/s04_08_create_ecr_repository.py
       :language: python
       :linenos:

这个脚本只是 `aws_ops_alpha <https://github.com/MacHu-GWU/aws_ops_alpha-project/blob/main/aws_ops_alpha/project/simple_lbd_container/step.py>`_ 中的函数的一个 wrapper, 把本项目相关的参数传递给了 ``create_ecr_repository`` 函数而已. 你可以查看源代码来李了解是如何创建 ECR Repository 并自动配置 cross account permission, 使得你可以在 Workload account 中的 Lambda Function 来访问这个 ECR Repository.
