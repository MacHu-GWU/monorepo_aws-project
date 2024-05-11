Data Ingestion
==============================================================================


Overview
------------------------------------------------------------------------------
这个模块的任务是将各种各样的数据源中将文档数据写入到 Landing Zone 中. 对于不同的数据源, 不同的文档类型, 我们的处理方法业不同. 这个模块本质上是一堆传统 ETL Pipeline 的集合 (每个 Pipeline 对应一个数据源). 这些 Pipeline 的 ingestion pattern 大体可以分为下面几类.

按照获取数据的方式分为:

- Push: 数据源把数据自动推到 pipeline 中
- Pull: pipeline 中的 worker 主动去数据源中拉取数据

按照 ETL 的方式分为:

- Batch
- Near real time
- Real time

对两种方式排列组合会构成 6 种模式.

我们如果以 Email 数据源举例, 我们的 Ingestion pattern 应该是 Near real time + Pull, 也就是 worker 隔上 1 分钟就去邮件服务器上拉取新邮件.
