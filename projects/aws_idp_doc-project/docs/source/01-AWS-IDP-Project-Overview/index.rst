AWS IDP Project Overview
==============================================================================


Overview
------------------------------------------------------------------------------
这是我在 AWS 工作时为大型企业生产环境设计的一套的 Intelligent Document Process (智能文档处理) 平台. 这套 Solution 已经被多个 AWS 的客户部署在了生产环境中, 并运行良好 1 年多了. 不同的企业中对于 CI/CD 工具, App Host 方案, Data Integration 和 Network Connectivity 各有不同. 而这个项目则是将这个 Solution 通用的, 核心的部分封装成了模块. 在模块的基础上只要进行非常简单的封装就可以适用于特定企业的特定环境.

本项目详细记录了这套 Solution 的架构. 并简略介绍了所有模块.


AWS IDP Project
------------------------------------------------------------------------------
AWS IDP 项目由多个可单独部署的模块组成:

- `aws_idp_doc-project`: 项目文档.
- `aws_idp_doc_store-project`: data ingestion, document data pre-processing, document data storage.
- `aws_idp_annotator-project`: 负责给数据打标签, 用于训练模型.
- `aws_idp_hil-project`: 人工审核 ML 模型的预测结果, 以及审核 data extraction 的结果.
- `aws_idp_doc_classify-project`: 对文档进行分类的 ML 模型.
- `aws_idp_data_extract-project`: 从文档中提取数据的程序.


Related Open Source Project
------------------------------------------------------------------------------
- `amazon-textract-textractor <https://github.com/aws-samples/amazon-textract-textractor>`_: AWS Textract 的 Python SDK 封装. 用于解析 Textract response object 并从中提取数据. 由 AWS 维护.
- `aws_textract_pipeline <https://github.com/MacHu-GWU/aws_textract_pipeline-project>`_: 这套 Solution 的底层 Python 实现. 不包含 AWS 的服务, 只是在内存里的纯计算. 这套实现可以用任何平台部署, 不局限于 AWS 平台. 并且既可以用虚拟机或容器的形式作为 Batch Job 部署, 也可以用 Event driven 的架构用于实时处理. 由 Sanhe Hu 维护.


Architecture Diagram
------------------------------------------------------------------------------
.. raw:: html
    :file: ./Intelligent-Document-Processing-Solution-Design.drawio.html
