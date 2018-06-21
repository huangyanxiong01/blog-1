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

本文以 GDB 调试可执行文件为例，介绍 GDB 最基本的使用流程：使用前准备 --> 启动 --> 设置 (设置断点 / 设置监控点) --> 运行 (单步调试 / continue 调试) --> 查看 (栈帧显示 / 值显示 / 修改变量值) --> 结束调试

待调试源码 `demo.c` 如下：

```
#include <stdio.h>

int main(void)
{
	int num1 = 1;
  num1 = 2;
	int num2 = 2;
	int result = num1 + num2;
	int var1 = 0;
	printf("%d\n", result);
	
	return 0;
}
```

#### 1. 使用前准备

因为以调试可执行文件为例，所以在编译构建源码时需要带着调试选项，有三种情况：

- 通过 `gcc` 编译构建：`gcc -Wall -g demo.c -o demo`
- 通过 configure 脚本生成 Makefile：./configure CFLAGS="-Wall -g"
- 通过 Makefile 构建：加上参数 CFLAGS = -Wall -g

#### 2. 启动

2.1. gdb + 可执行文件名，看到提示符 `(gdb)` 即可。演示如下：

```
shell> gdb demo
GNU gdb (Ubuntu 7.7.1-0ubuntu5~14.04.3) 7.7.1
Copyright (C) 2014 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
<http://www.gnu.org/software/gdb/documentation/>.
For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from demo...done.
(gdb)
```

2.2. 运行 `start` 命令 (非必须，方便设置监控点)，默认进入到 `main` 函数。演示如下

```
(gdb) start
Temporary breakpoint 1 at 0x400535: file demo.c, line 5.
Starting program: /root/demo 

Temporary breakpoint 1, main () at demo.c:5
5		int num1 = 1;
(gdb)
```

#### 3. 设置

3.1 设置断点

命令 `break` 简写 `b` + 断点位置，具体支持的格式如下：

- b 函数名
- b 行号
- b 文件名:函数名
- b 文件名:行号
- b +当前位置的偏移量
- b -当前位置的偏移量
- b *内存地址 (16 进制)



































