1. 解决多个 aws_ops_alpha.project 里的几个模块互相 import 的时候 step, branch, env, runtime 不一样如何兼容的问题.
2. 重新设计 automation 下面的 bin, 尽量做到 0 依赖也能使用, 连 pyproject_ops 也不需要安装
3. 测试 github workflow 的 simple_release
4. 解决 cookiecutter 没有模板化 github workflow yaml 的问题.