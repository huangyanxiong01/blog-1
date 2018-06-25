### 概述

当进程异常结束时，core dump 能记录下进程当时的状态，以供之后的调试。常见的用途有：崩溃后的调试保障、难以复现的问题、非常罕见的问题。总之，只要有可执行文件和 core dump，就能够最大程度上保证可调试。

---

### 开启 core dump

#### 1. 启动内核 core dump 功能

```
# 启动，并且不限制 core 文件的大小
shell> ulimit -c unlimited
shell> echo 1 > /proc/sys/kernel/core_uses_pid

# 启动，但限制 core 文件大小为 1G
shell> ulimit -c 1073741824
```

#### 2. 压缩 core 文件并统一放到专用目录下

```
# 编写压缩脚本
1. vim /usr/local/sbin/coredump_helper
2. 输入如下内容：
#!/bin/bash
exec gzip - > /var/core/$1-$2-$3-$4.core.gz

# 编辑内核配置文件
shell> sysctl -w kernel.core_pattern="|/usr/local/sbin/coredump_helper %t %e %p %c"
shell> sysctl -p
```

kernel.core_pattern 支持的格式符：

- %t：core dump 时间
- %e：可执行文件名称
- %p：pid
- %c：core 文件大小上限

验证一下，运行下面这段代码，就会在 `/var/core` 目录下发现压缩后的 core 文件了。

```
#include <stdlib.h>
#include <stdio.h>


int main(void)
{
	int *x = malloc(10);
	free(x);
	free(x);
	return 0;
}
```

#### 3. 配置启动脚本确保开启


```
1. vim /etc/rc.local
2. 输入如下内容：
ulimit -c unlimited
echo 1 > /proc/sys/kernel/core_uses_pid
sysctl -w kernel.core_pattern="|/usr/local/sbin/coredump_helper %t %e %p %c"
sysctl -p
```

#### 4. GDB 使用 core 文件

以 2 中的测试代码为例，演示 GDB 如何使用 core 文件进行调试。

```
