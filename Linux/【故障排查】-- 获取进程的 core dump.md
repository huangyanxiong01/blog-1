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
# demo5.c

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
shell> gdb demo5 1529921578-demo5-1386-18446744073709551615.core

...

# 查看栈
(gdb) bt
#0  0x00007f1775d3ac37 in __GI_raise (sig=sig@entry=6) at ../nptl/sysdeps/unix/sysv/linux/raise.c:56
#1  0x00007f1775d3e028 in __GI_abort () at abort.c:89
#2  0x00007f1775d772a4 in __libc_message (do_abort=do_abort@entry=1, fmt=fmt@entry=0x7f1775e89350 "*** Error in `%s': %s: 0x%s ***\n")
    at ../sysdeps/posix/libc_fatal.c:175
#3  0x00007f1775d8382e in malloc_printerr (ptr=<optimized out>, str=0x7f1775e89518 "double free or corruption (fasttop)", action=1) at malloc.c:4998
#4  _int_free (av=<optimized out>, p=<optimized out>, have_lock=0) at malloc.c:3842
#5  0x00000000004005ab in main () at demo5.c:9

# 切换栈
(gdb) frame 5
#5  0x00000000004005ab in main () at demo5.c:9
9		free(x);

# 查看对应位置的源码
(gdb) list 9
4	
5	int main(void)
6	{
7		int *x = malloc(10);
8		free(x);
9		free(x);
10		return 0;
11	}

# 发现双重释放
```

