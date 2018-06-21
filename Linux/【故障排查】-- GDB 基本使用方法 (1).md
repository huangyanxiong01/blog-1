### <font color=#00b0f0>运行环境</font>

```
# uname -a
Linux ubuntu 3.16.0-30-generic #40~14.04.1-Ubuntu SMP Thu Jan 15 17:43:14 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux

# cat /etc/*-release
DISTRIB_DESCRIPTION="Ubuntu 14.04.2 LTS"

# 内存：2G
# CPU：2核
# GDB: 7.7.1
```

---

### 概述

虽然每种编程语言都或多或少有一套自己的调试工具，在实际解决问题时也应该优先考虑这些工具。但是 GDB 作为 Linux 环境下的标准调试器，只要你的应用需要跑在 Linux 下，那么了解如何使用 GDB 还是非常有必要的，因为在其他工具都无法提供帮助的时候，回归平台原生的工具或许是个好选择。

本文以 GDB 调试可执行文件为例，介绍 GDB 最基本的使用流程：使用前准备 --> 启动 GDB --> 设置断点 / 设置监控点 --> 单步调试 / continue 调试 --> 栈帧显示 / 值显示 / 修改变量值 --> 结束调试


#### 1. 
