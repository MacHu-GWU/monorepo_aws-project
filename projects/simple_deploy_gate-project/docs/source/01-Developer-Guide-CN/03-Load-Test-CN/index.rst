Load Test (CN)
==============================================================================
这个项目是一个 API Server 的项目. 那么自然而然地就要考虑 API 的并发问题. 你需要确保你的 API Gateway 能在短时间内处理大量并发, 并且底层的 Lambda Function 也同样能应付这些流量, 所以 Load Test (压力测试) 是必不可少的.

`Python locust <https://locust.io/>`_ 是一个纯 Python 的压力测试工具. 它基于 twisted 异步框架, 可以用很小的 CPU 资源就能模拟大量并发. 使用 locust 的方法也很简单, 你需要定义一个 ``locustfile``, 里面定义了 Request 的请求. 然后在命令行中执行 ``locust -f locustfile.py`` 就可以启动压力测试了. 命令行会将 locustfile 中的函数用一个类包装起来, 使得它的行为变为异步, 然后 locust 将其放到一个协程中执行, 从而实现并发. 而 locust 自带一个 Web UI 可以用来查看并发的统计数据. 值得注意的是, locust 不仅支持 HTTP Request, 还支持其他的抽象 Request, 只要这个 Request 是 IO intense 的, 就可以被 locust 模拟.

在我们这个项目中我们实现了 ``tests_load/locustfile_slow.py`` 和 ``tests_load/locustfile_fast.py`` 两个 locustfile. 分别用比较慢的 HTTP client 和比较快的 HTTP client 来发送请求. 然后我们可以用 ``bin/s05_01_run_load_test.py`` 这个 Shell Script 来启动 load test.
