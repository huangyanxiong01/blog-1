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

本文以 GDB 调试可执行文件为例，介绍 GDB 最基本的使用流程：使用前准备 --> 启动 --> 设置 (设置断点 / 设置监控点) --> 运行 (单步运行 / continue 运行) <--> 查看 (查看栈帧 / 查看变量值 / 查看某个栈帧) --> 结束调试

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

---

### 使用

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

断点的作用：当进程运行到断点处的时候会暂停运行，此时可以查看该时刻的变量值、栈帧。3.1~3.3 是断点相关的操作。

3.1 设置断点

`break` (简写 `b`) + 断点位置。具体支持的格式如下：

- b 函数名
- b 行号
- b 文件名:函数名
- b 文件名:行号
- b +当前位置的偏移量
- b -当前位置的偏移量
- b *内存地址 (16 进制)

演示如下：

```
# 在 printf 函数调用处设置断点
(gdb) b printf
Breakpoint 2 at 0x7ffff7a65340: file printf.c, line 28.
(gdb)
```

3.2. 查看断点

演示如下：

`info` + `b`。演示如下：

```
(gdb) info b
Num     Type           Disp Enb Address            What
2       breakpoint     keep y   0x00007ffff7a65340 in __printf at printf.c:28
(gdb) 
```

3.3. 删除断点

`d` + 断点的 Num。演示如下：

```
(gdb) d 2
(gdb)
(gdb) info b
No breakpoints or watchpoints.
(gdb) 
```

监控点的作用：实际环境下变量的值可能会被大量地传递和修改，想要人为去观察是很累的，监控点就是帮助我们跟踪变量的变化的，当有变化时就会暂停下来等待我们检查。3.4~3.6 是监控点相关操作。

3.4. 设置监控点

`watch/awatch/rwatch` + 表达式 (一般就是变量名了)。支持的格式如下：

- `watch` + 变量名：当变量被写时暂停
- `rwatch` + 变量名：当变量被读时暂停
- `awatch` + 变量名：当变量被读或写时暂停

演示如下：

```
# 给 result 变量设置读监控点
(gdb) rwatch result
Hardware read watchpoint 3: result
(gdb)
# 源码第 10 行 printf("%d\n", result); 读变量了，所以在此处暂停了下来
(gdb) c
Continuing.
Hardware read watchpoint 3: result

Value = 4
0x000000000040055f in main () at demo.c:10
10		printf("%d\n", result);
(gdb) 
```

3.5. 查看监控点

`info watch`。演示如下：


```
(gdb) info watch       
Num     Type            Disp Enb Address    What
4       read watchpoint keep y              result
```

3.6. 删除监控点

`d` + 监控点 Num。演示如下：

```
(gdb) d 4
(gdb) info watch
No watchpoints.
(gdb)
```

#### 4. 运行

4.1. 单步运行

也就是按照代码的逻辑顺序一步步地运行，会在每一步都暂停下来。对应命令简写 `n`。演示如下：

```
(gdb) start
Temporary breakpoint 1 at 0x400535: file demo.c, line 5.
Starting program: /root/demo 

Temporary breakpoint 1, main () at demo.c:5
5		int num1 = 1;
(gdb) n
6	  	num1 = 2;
(gdb) n
7		int num2 = 2;
(gdb) n
8		int result = num1 + num2;
(gdb) n
9		int var1 = 0;
(gdb) n
10		printf("%d\n", result);
(gdb) n
4
12		return 0;
(gdb) n
13	}
(gdb) n
__libc_start_main (main=0x40052d <main>, argc=1, argv=0x7fffffffe6a8, init=<optimized out>, fini=<optimized out>, rtld_fini=<optimized out>, 
    stack_end=0x7fffffffe698) at libc-start.c:321
321	libc-start.c: ?????????.
(gdb) n
[Inferior 1 (process 2639) exited normally]
(gdb) n
The program is not being run.
(gdb) 
```

需要注意的是，当 GDB 显示 `8		int result = num1 + num2;` 时指的不是运行完这一步，而是将要运行这一步。比如下面的代码片段中，在 `8		int result = num1 + num2;` 之后输出 result 变量的值 (`p result`) 发现还是 0，只有当执行到 `9		int var1 = 0;` 后，result 变量的值才是 4。演示如下：

```
(gdb) start 
Temporary breakpoint 4 at 0x400535: file demo.c, line 5.
Starting program: /root/demo 

Temporary breakpoint 4, main () at demo.c:5
5		int num1 = 1;
(gdb) n
6	  	num1 = 2;
(gdb) n
7		int num2 = 2;
(gdb) n
8		int result = num1 + num2;
(gdb) p result
$2 = 0
(gdb) n
9		int var1 = 0;
(gdb) p result
$3 = 4
(gdb) 
```

4.2. continue 运行

相比单步运行的每一步都会暂停，continue 运行只会在断点处，或者监控点处暂停。对应命令简写 `c`。演示如下：

```
# 在 printf 函数调用处设置了断点，在 printf 处暂停
(gdb) start
Temporary breakpoint 5 at 0x400535: file demo.c, line 5.
Starting program: /root/demo 

Temporary breakpoint 5, main () at demo.c:5
5		int num1 = 1;
(gdb) b printf
Breakpoint 6 at 0x7ffff7a65340: file printf.c, line 28.
(gdb) c
Continuing.

Breakpoint 6, __printf (format=0x400604 "%d\n") at printf.c:28
28	printf.c: ?????????.
(gdb) 

# 没有设置断点，直接运行结束
(gdb) start
Temporary breakpoint 8 at 0x400535: file demo.c, line 5.
Starting program: /root/demo 

Temporary breakpoint 8, main () at demo.c:5
5		int num1 = 1;
(gdb) c
Continuing.
4
[Inferior 1 (process 2659) exited normally]
(gdb) c
The program is not being run.
(gdb) 
```

#### 5. 查看

5.1. 查看栈帧

命令简写 `bt`。支持的格式如下：

- bt：显示该时刻所有的栈帧
- bt full：显示该时刻所有的栈帧和局部变量
- bt N：显示该时刻前 N 个栈帧
- bt -N：显示该时刻倒数 N 个栈帧
- bt full N：同理
- bt fill -N：同理

演示如下：

```
(gdb) start
Temporary breakpoint 12 at 0x400535: file demo.c, line 5.
Starting program: /root/demo 

Temporary breakpoint 12, main () at demo.c:5
5		int num1 = 1;

# 设置断点
(gdb) b printf
Breakpoint 13 at 0x7ffff7a65340: file printf.c, line 28.

# continue 运行
(gdb) c
Continuing.

# 断点处暂停
Breakpoint 13, __printf (format=0x400604 "%d\n") at printf.c:28
28	printf.c: ?????????.

# 查看所有栈帧
(gdb) bt 
#0  __printf (format=0x400604 "%d\n") at printf.c:28
#1  0x0000000000400570 in main () at demo.c:10

# 查看所有栈帧和局部变量
(gdb) bt full
#0  __printf (format=0x400604 "%d\n") at printf.c:28
        arg = {{gp_offset = 4160689488, fp_offset = 32767, overflow_arg_area = 0x1, reg_save_area = 0x601018 <printf@got.plt>}}
        done = 0
#1  0x0000000000400570 in main () at demo.c:10
        num1 = 2
        num2 = 2
        result = 4
        var1 = 0
(gdb) 
```

5.2. 查看变量值

命令简写 `p` (其实 `bt full` 也多多少少有这个功能了)。演示如下：

```
(gdb) c
Continuing.

Breakpoint 1, main () at demo.c:9
9		int var1 = 0;
(gdb) p num1
$1 = 2
(gdb) p num2
$2 = 2
(gdb) p result
$3 = 4
```

5.3. 查看某个栈帧

命令：info + 栈帧编号，如 `info #1`。

#### 6. 其他小技巧

- 修改变量值：在进程运行时动态修改变量的值，无需改变源码就可以验证一些东西。命令 `set variable 变量名 = 值`
- 生成 core dump 文件：将本次调试的过程 (进程的运行过程) 保存起来。命令 `generate-core-file`













