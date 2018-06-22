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

[【故障排查】-- GDB 基本使用方法 (1)](https://github.com/hsxhr-10/blog/blob/master/Linux/【故障排查】--%20GDB%20基本使用方法%20(1).md) 中以调试可执行程序为例，介绍了 GDB 的基本使用方法。本文主要介绍 GDB 的另外一种调试形式 attach，这种形式适用于已经运行的进程，**常见的场景有：单纯逻辑错误导致的死循环、I/O 阻塞、死锁。症状为系统负载高、CPU 占用率高、进程无响应。**

attach 使用流程：定位待调试进程的 pid --> 启动 --> attach <pid> --> GDB 基本操作

待调试源码 `mock_high_cpu_load.c` 如下：

```
#include <stdio.h>

int main(void)
{
	while(1)
	{
		printf("%s", "hello");
	}

	return 0;
}
```

---

### 使用技巧

#### 1. 定位 pid

通过 `top` 命令定位 pid。演示如下：

```
shell> top

top - 20:25:53 up  8:06,  4 users,  load average: 0.39, 0.13, 0.08
Tasks: 178 total,   5 running, 173 sleeping,   0 stopped,   0 zombie
%Cpu0  : 23.4 us, 14.1 sy,  0.0 ni, 62.5 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
%Cpu1  : 31.3 us, 15.6 sy,  0.0 ni, 49.0 id,  0.0 wa,  0.0 hi,  4.1 si,  0.0 st
KiB Mem:   1014068 total,   379688 used,   634380 free,    17824 buffers
KiB Swap:  1044476 total,        0 used,  1044476 free.   261048 cached Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                                                                
 3099 root      20   0    4208    620    552 R  48.9  0.1   0:05.50 mock_high_cpu_l 
```

#### 2. 启动

直接 `gdb` 即可。演示如下：

```
shell> gdb
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
Type "apropos word" to search for commands related to "word".
(gdb) 
```

#### 3. attach pid

`attach` + <pid>。演示如下：
	
```
(gdb) attach 3099
Attaching to process 3099
Reading symbols from /root/mock_high_cpu_load...(no debugging symbols found)...done.
Reading symbols from /lib/x86_64-linux-gnu/libc.so.6...Reading symbols from /usr/lib/debug//lib/x86_64-linux-gnu/libc-2.19.so...done.
done.
Loaded symbols for /lib/x86_64-linux-gnu/libc.so.6
Reading symbols from /lib64/ld-linux-x86-64.so.2...Reading symbols from /usr/lib/debug//lib/x86_64-linux-gnu/ld-2.19.so...done.
done.
Loaded symbols for /lib64/ld-linux-x86-64.so.2
0x00007f38c9bea3c0 in __write_nocancel () at ../sysdeps/unix/syscall-template.S:81
81	../sysdeps/unix/syscall-template.S: ?????????.
(gdb) 
```

#### 4. GDB 基本操作

下面就可以进行一些 GDB 的基本操作了。连续 3 次 bt，出现重复的栈帧，确定存在死循环，留意栈帧中的 `#7` 定位出了死循环点。演示如下：

```
# 第 1 次
(gdb) bt
#0  0x00007f3926c5d3c0 in __write_nocancel () at ../sysdeps/unix/syscall-template.S:81
#1  0x00007f3926be6f13 in _IO_new_file_write (f=0x7f3926f31400 <_IO_2_1_stdout_>, data=0x7f3927158000, n=1024) at fileops.c:1261
#2  0x00007f3926be83ec in new_do_write (to_do=1024, 
    data=0x7f3927158000 "lohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohel"..., fp=0x7f3926f31400 <_IO_2_1_stdout_>) at fileops.c:538
#3  _IO_new_do_write (fp=0x7f3926f31400 <_IO_2_1_stdout_>, 
    data=0x7f3927158000 "lohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohel"..., to_do=1024) at fileops.c:511
#4  0x00007f3926be75b1 in _IO_new_file_xsputn (f=0x7f3926f31400 <_IO_2_1_stdout_>, data=<optimized out>, n=5) at fileops.c:1332
#5  0x00007f3926bb9905 in _IO_vfprintf_internal (s=<optimized out>, format=<optimized out>, ap=ap@entry=0x7fffe32c5738) at vfprintf.c:1661
#6  0x00007f3926bc23d9 in __printf (format=<optimized out>) at printf.c:33
#7  0x0000000000400545 in main () at mock_high_cpu_load.c:7

# 第 2 次
(gdb) bt
#0  0x00007f3926c5d3c0 in __write_nocancel () at ../sysdeps/unix/syscall-template.S:81
#1  0x00007f3926be6f13 in _IO_new_file_write (f=0x7f3926f31400 <_IO_2_1_stdout_>, data=0x7f3927158000, n=1024) at fileops.c:1261
#2  0x00007f3926be83ec in new_do_write (to_do=1024, 
    data=0x7f3927158000 "lohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohel"..., fp=0x7f3926f31400 <_IO_2_1_stdout_>) at fileops.c:538
#3  _IO_new_do_write (fp=0x7f3926f31400 <_IO_2_1_stdout_>, 
    data=0x7f3927158000 "lohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohel"..., to_do=1024) at fileops.c:511
#4  0x00007f3926be75b1 in _IO_new_file_xsputn (f=0x7f3926f31400 <_IO_2_1_stdout_>, data=<optimized out>, n=5) at fileops.c:1332
#5  0x00007f3926bb9905 in _IO_vfprintf_internal (s=<optimized out>, format=<optimized out>, ap=ap@entry=0x7fffe32c5738) at vfprintf.c:1661
#6  0x00007f3926bc23d9 in __printf (format=<optimized out>) at printf.c:33
#7  0x0000000000400545 in main () at mock_high_cpu_load.c:7

# 第 3 次
(gdb) bt
#0  0x00007f3926c5d3c0 in __write_nocancel () at ../sysdeps/unix/syscall-template.S:81
#1  0x00007f3926be6f13 in _IO_new_file_write (f=0x7f3926f31400 <_IO_2_1_stdout_>, data=0x7f3927158000, n=1024) at fileops.c:1261
#2  0x00007f3926be83ec in new_do_write (to_do=1024, 
    data=0x7f3927158000 "lohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohel"..., fp=0x7f3926f31400 <_IO_2_1_stdout_>) at fileops.c:538
#3  _IO_new_do_write (fp=0x7f3926f31400 <_IO_2_1_stdout_>, 
    data=0x7f3927158000 "lohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohellohel"..., to_do=1024) at fileops.c:511
#4  0x00007f3926be75b1 in _IO_new_file_xsputn (f=0x7f3926f31400 <_IO_2_1_stdout_>, data=<optimized out>, n=5) at fileops.c:1332
#5  0x00007f3926bb9905 in _IO_vfprintf_internal (s=<optimized out>, format=<optimized out>, ap=ap@entry=0x7fffe32c5738) at vfprintf.c:1661
#6  0x00007f3926bc23d9 in __printf (format=<optimized out>) at printf.c:33
#7  0x0000000000400545 in main () at mock_high_cpu_load.c:7
(gdb) 
```

此时还可以进行设置断点、设置监控点、查看变量值等操作。

还可以通过 `info proc` 查看进程的基本信息。演示如下：

```
(gdb) info proc
process 3158
cmdline = './mock_high_cpu_load'
cwd = '/root'
exe = '/root/mock_high_cpu_load'
```













