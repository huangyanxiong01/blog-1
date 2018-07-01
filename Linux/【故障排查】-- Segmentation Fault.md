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

本文讨论了**Segmentation Fault 导致程序异常结束**的调试方法。

虽然下面的工具以 c 环境为基础，但是 c 作为系统语言，很多高级语言或者组件都是 c 写的，所以学会这些工具其实也是一个比较通用的技能。

本文的思路为：通过 GDB 识别内存问题 --> 通过 Valgrind 定位内存问题 (源码位置)。

---

### 通过 GDB 识别内存问题

*注意：下面 GDB 调试默认依赖了程序崩溃时生成的 core dump 文件，且被调试的程序都加了 -g 参数去编译构建。*

#### 1. 栈溢出

常见于超出了栈大小的递归调用。

通过 GDB 可以看到同一个函数被同一个地址重复调用。演示如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/栈溢出1.png)

#### 2. 栈被破坏

常见于多线程环境下的线程冲突、向已分配的内存空间之外写数据。

在编译构建时已经加了 `-g` 参数表明可调式的情况下，如果通过 GDB 还是看到如下 backtrace 信息异常，说明栈被破坏了，即使有部分栈信息可见，也不应该信任。演示如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/栈被破坏1.png)

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/栈被破坏2.png)

---

### 通过 Valgrind 定位内存问题

#### 1. 内存泄漏

演示代码如下：

```
shell> cat -n ./demo1.c
     1	#include <stdio.h>
     2	#include <stdlib.h>
     3	
     4	
     5	int main(void)
     6	{
     7		char *p = malloc(10);
     8		return 0;
     9	}
    10	
```

演示如下：

```
shell> valgrind --leak-check=yes ./demo1

==6719== Memcheck, a memory error detector
==6719== Copyright (C) 2002-2013, and GNU GPL'd, by Julian Seward et al.
==6719== Using Valgrind-3.10.1 and LibVEX; rerun with -h for copyright info
==6719== Command: ./demo1
==6719== 
==6719== 
==6719== HEAP SUMMARY:
==6719==     in use at exit: 10 bytes in 1 blocks
==6719==   total heap usage: 1 allocs, 0 frees, 10 bytes allocated                             --- A
==6719== 
==6719== 10 bytes in 1 blocks are definitely lost in loss record 1 of 1                        --- B
==6719==    at 0x4C2AB80: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==6719==    by 0x40053E: main (demo1.c:7)                                                      
==6719== 
==6719== LEAK SUMMARY:
==6719==    definitely lost: 10 bytes in 1 blocks
==6719==    indirectly lost: 0 bytes in 0 blocks
==6719==      possibly lost: 0 bytes in 0 blocks
==6719==    still reachable: 0 bytes in 0 blocks
==6719==         suppressed: 0 bytes in 0 blocks
==6719== 
==6719== For counts of detected and suppressed errors, rerun with: -v
==6719== ERROR SUMMARY: 1 errors from 1 contexts (suppressed: 0 from 0)
```

留意 A 处 `total heap usage: 1 allocs, 0 frees, 10 bytes allocated` 中 allocs 和 frees 的个数，如果不相等那就存在内存泄漏的风险；观察 B 处已经明确地指出了内存泄漏发生的源码位置。

#### 2. 读写非法内存区域

演示代码如下：

```
shell> cat -n ./demo2.c 
     1	#include <stdlib.h>
     2	#include <stdio.h>
     3	
     4	
     5	int main(void)
     6	{
     7		char *p = malloc(10);
     8		p[10] = 1;
     9		printf("%c", p[20]);
    10		free(p);
    11		return 0;
    12	}
    13	
```

演示如下：

```
shell> valgrind --leak-check=full ./demo2

==7403== Memcheck, a memory error detector
==7403== Copyright (C) 2002-2013, and GNU GPL'd, by Julian Seward et al.
==7403== Using Valgrind-3.10.1 and LibVEX; rerun with -h for copyright info
==7403== Command: ./demo2
==7403== 
==7403== Invalid write of size 1                                      --- A
==7403==    at 0x4005DB: main (demo2.c:8)
==7403==  Address 0x520004a is 0 bytes after a block of size 10 alloc'd
==7403==    at 0x4C2AB80: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==7403==    by 0x4005CE: main (demo2.c:7)
==7403== 
==7403== Invalid read of size 1                                       --- B
==7403==    at 0x4005E6: main (demo2.c:9)
==7403==  Address 0x5200054 is 10 bytes after a block of size 10 alloc'd
==7403==    at 0x4C2AB80: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==7403==    by 0x4005CE: main (demo2.c:7)
==7403== 
==7403== 
==7403== HEAP SUMMARY:
==7403==     in use at exit: 0 bytes in 0 blocks
==7403==   total heap usage: 1 allocs, 1 frees, 10 bytes allocated    --- C
==7403== 
==7403== All heap blocks were freed -- no leaks are possible          --- D
==7403== 
==7403== For counts of detected and suppressed errors, rerun with: -v
==7403== ERROR SUMMARY: 2 errors from 2 contexts (suppressed: 0 from 0)
```

留意 A 处检测出非法的写操作，并明确指出了对应源码位置；B 处也检测出了非法的读操作，也指出了对应的源码位置。同时，C/D 处都表明没有内存泄漏。

#### 3. 读未初始化的内存区域

演示代码如下：

```
shell> cat -n ./demo3.c
     1	#include <stdlib.h>
     2	#include <stdio.h>
     3	
     4	
     5	int main(void)
     6	{
     7		int *x = malloc(10);
     8		printf("%d", *x);
     9		free(x);
    10		return 0;
    11	}
    12	
```

演示如下：

```
shell> valgrind --leak-check=full ./demo3

...

==7451== Conditional jump or move depends on uninitialised value(s)        --- A
==7451==    at 0x4E814CE: vfprintf (vfprintf.c:1660)
==7451==    by 0x4E8B3D8: printf (printf.c:33)
==7451==    by 0x4005E9: main (demo3.c:8)
==7451== 
==7451== Use of uninitialised value of size 8                              --- B
==7451==    at 0x4E8099B: _itoa_word (_itoa.c:179)
==7451==    by 0x4E84636: vfprintf (vfprintf.c:1660)
==7451==    by 0x4E8B3D8: printf (printf.c:33)
==7451==    by 0x4005E9: main (demo3.c:8)

...
```

A/B 处都检测出读取了未初始化的内存区域，且指出了对应的源码位置。

#### 4. 读已释放的内存区域

演示代码如下：

```
shell> cat -n ./demo4.c
     1	#include <stdlib.h>
     2	#include <stdio.h>
     3	
     4	
     5	int main(void)
     6	{
     7		int *x = malloc(10);
     8		*x = 1;
     9		printf("%d\n", *x);
    10		free(x);
    11		printf("%d\n", *x);
    12		return 0;
    13	}
```

演示如下：

```
shell> valgrind --leak-check=full ./demo4

...

==7479== Invalid read of size 4                        --- A
==7479==    at 0x400604: main (demo4.c:11)
==7479==  Address 0x5200040 is 0 bytes inside a block of size 10 free'd
==7479==    at 0x4C2BDEC: free (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==7479==    by 0x4005FF: main (demo4.c:10)

...
```

A 处检测出非法读操作，且指出了对应的源码位置。

#### 5. 内存双重释放

演示代码如下：

```
shell> cat -n ./demo5.c
     1	#include <stdlib.h>
     2	#include <stdio.h>
     3	
     4	
     5	int main(void)
     6	{
     7		int *x = malloc(10);
     8		free(x);
     9		free(x);
    10		return 0;
    11	}
```

演示如下：

```
shell> valgrind --leak-check=full ./demo5

...

==7502== Invalid free() / delete / delete[] / realloc()               --- A
==7502==    at 0x4C2BDEC: free (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==7502==    by 0x4005AA: main (demo5.c:9)
==7502==  Address 0x5200040 is 0 bytes inside a block of size 10 free'd
==7502==    at 0x4C2BDEC: free (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==7502==    by 0x40059E: main (demo5.c:8)

...
```

A 处检测出内存双重释放操作，且明确指出了对应的源码位置。





