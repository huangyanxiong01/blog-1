### 概述

当进程异常结束时，core dump 能记录下进程当时的状态，以供之后的调试。常见的用途有：崩溃后的调试保障、难以复现的问题、非常罕见的问题。总之，只要有可执行文件和 core dump，就能够最大程度上保证可调试。

---

### 开启 core dump

#### 1. 启动内核 core dump 功能

```
# 0 代表内核还没启动该功能
shell> ulimit -c
0

# 启动，并且不限制 core 文件的大小
shell> ulimit -c unlimited

# 启动，但限制 core 文件大小为 1G
shell> ulimit -c 1073741824
```

#### 2. 压缩 core 文件并统一放到专用目录下

```
# 编写压缩脚本
1. vim /usr/local/sbin/coredump_helper
2. 输入如下内容
    #!/bin/bash
    exec gzip - > /var/core/$1-$2-$3-$4.core.gz


shell> ssysctl -w kernel.core_pattern="|/usr/local/sbin/coredump_helper %t %e %p %c"
shell> ssysctl -p
```












