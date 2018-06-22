### 运行环境

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

本文主要介绍 GDB 使用小技巧，分别是：条件断点、值的记录。

#### 1. 条件断点

当某个条件为真时才触发断点。命令格式：`b 断点位置 if 条件`。

演示如下：

```
# 在源码第 9 行设置断点，条件是当变量 result 的值等于 4 时触发断点
(gdb) b 9 if result == 4
Breakpoint 2 at 0x400555: file demo.c, line 9.
(gdb) info b
Num     Type           Disp Enb Address            What
2       breakpoint     keep y   0x0000000000400555 in main at demo.c:9
	stop only if result == 4
(gdb) c
Continuing.

Breakpoint 2, main () at demo.c:9
9		int var1 = 0;
(gdb)
```

#### 2. 值的记录

输出过的值都会被 GDB 记录下来，可供之后的操作使用。

命令格式：

- show values：显示所有值记录
- $：显示最后一个值记录
- $n：显示第 n 个值记录

演示如下：

```
# 没有值记录时
(gdb) show values 
(gdb) 

# 输出一些值
(gdb) p num1
$1 = 2
(gdb) p num2
$2 = 2
(gdb) p var1  
$3 = 0
(gdb) p result
$4 = 4

# 再次查看值记录
(gdb) show values 
$1 = 2
$2 = 2
$3 = 0
$4 = 4

# 分别查看值记录
(gdb) p $
$5 = 4
(gdb) p $1
$6 = 2
(gdb) p $2
$7 = 2
(gdb) p $3
$8 = 0
(gdb) p $4
$9 = 4
(gdb) 
```

#### 3. 值的记录配合条件断点使用

演示如下：

```
# 单步运行，运行到代码的第 7 行。此时 num1 的值是 2
(gdb) info b
No breakpoints or watchpoints.
(gdb) n 
6	  	num1 = 2;
(gdb) p num1
$1 = 1
(gdb) n
7		int num2 = 2;
(gdb) p num1
$2 = 2

# 利用变量记录 $2，在第 10 行设置一个断点 (即当 result 的值等于 2+2 时，触发断点)
(gdb) show values             
$1 = 1
$2 = 2
$3 = 32767
(gdb) b 10 if result == $2+$2
Breakpoint 2 at 0x40055c: file demo.c, line 10.
(gdb) info b
Num     Type           Disp Enb Address            What
2       breakpoint     keep y   0x000000000040055c in main at demo.c:10
	stop only if result == $2+$2
(gdb) 

# 触发断点成功
(gdb) c
Continuing.

Breakpoint 2, main () at demo.c:10
10		printf("%d\n", result);
(gdb)
```










