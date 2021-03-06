### <font color=#00b0f0>运行环境</font>

```
# uname -a
Linux ubuntu 3.16.0-30-generic #40~14.04.1-Ubuntu SMP Thu Jan 15 17:43:14 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux

# python2 --version
Python 2.7.9

# cat /etc/*-release
DISTRIB_DESCRIPTION="Ubuntu 14.04.2 LTS"

# 内存：2G
# CPU：2核
```

---

### <font color=#00b0f0>触发 OOM</font>

在[【故障排查】-- python 内存泄漏](https://github.com/hsxhr-10/blog/blob/master/Linux/【故障排查】--%20python%20内存泄漏.md)
中，我们聚焦的是如何对高内存占用问题进行排查。现在换一个角度，假设有疯狂占用内存的进程，我们不管这个进程会是什么结果？系统会因为这个内存泄漏的进程而崩溃吗？
其实不然，内核会通过 OOM Killer 机制去处理这个进程

所谓的 OOM Killer 机制就是系统的一种自我保护机制，当内存严重不足时，内核通过杀掉占用内存最多的进程来释放掉内存，从而让系统不至于因为内存不足而马上崩溃。

下面将使用 `bootup_oom.c` 来触发 OOM 机制，代码如下：

```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PAGE_SZ (1<<12)

int main() {
    int i;
    int gb = 1;

    for (i = 0; i < ((unsigned long)gb<<30)/PAGE_SZ ; ++i) {
        void *m = malloc(PAGE_SZ);
        if (!m) {
            break;
        }
        memset(m, 0, 1);
    }

    return 0;
}
```

编译并执行代码：

```
gcc mock_oom.c
./a.out
```

大概 1 秒钟之后可以观察到控制台的变化：

```
root@ubuntu:/opt# ./a.out 
Killed
```

查看 `/var/log/dmesg` 日志文件，可以看到进程 `5325` 也就是程序 `a.out` 已经触发了 OOM 并成功被 kill：

```
root@ubuntu:/var/log# dmesg -T | grep "Out of memory"
[Sat May 19 23:36:37 2018] Out of memory: Kill process 5325 (a.out) score 799 or sacrifice child
```

---

### <font color=#00b0f0>配置 OOM</font>

虽然 OOM 是内核空间的事情，但是我们也可以在用户空间去做一些修改和配置。对于 OOM 有 4 种对应的处理方式：

- 默认方式：让内核去 Kill 掉内存占用最多的进程
- 自动重启：当有进程触发 OOM 时，不采取默认方式，而是系统自动重启，通过 `vm.panic_on_oom` 和 `kernel.panic` 两个内核参数去控制。个人感觉这种随便重启的方式非常的不好，所以不做谈论
- 调整 `oom_adj` 参数：内核在执行 OOM Killer 时是根据 `points` 和 `oom_adj` 的总和去做判断的，总和越大的越容易被 kill 掉。(参考 [linux/mm/oom_kill.c](https://github.com/torvalds/linux/blob/master/mm/oom_kill.c) 的 `oom_badness` 函数)。

```
	# oom_badness 函数关于两个关键参数的截取

	...

	long points;
	long adj;

	...

	/*
	* The baseline for the badness score is the proportion of RAM that each
	* task's rss, pagetable and swap space use.
	*/
	points = get_mm_rss(p->mm) + get_mm_counter(p->mm, MM_SWAPENTS) +
					mm_pgtables_bytes(p->mm) / PAGE_SIZE;

	...

	points += adj;

	...

```

其中，`points` 是进程所占用的内存大小，而 `oom_adj` 是内核留给用户空间做调整的参数。比如 `points` 数值相差不多的两个进程 A 和 B，如果我不想让 B 那么容易被 OOM Killer 处理掉，我就可以把 B 的 `oom_adj` 参数设置得更小，`oom_adj` 的取值范围是 [-17, 15]，其中，-17 代表该进程不会被 OOM 杀死。例如我想让 dockerd 的服务不那么容易被 kill：

```
# 通过 ps 找到 PID
root@ubuntu:/var/log# ps aux | grep dockerd | grep -v color
root       956  0.1  1.9 372996 19844 ?        Ssl  May16   9:17 /usr/bin/dockerd --raw-logs

# 通过 /proc 找到进程的 oom_adj 值
root@ubuntu:/var/log# cat /proc/956/oom_adj
-8

# 改写 oom_adj 值
root@ubuntu:/var/log# echo > -16 /proc/956/oom_adj
```

- 关闭 OOM Killer：非常不推荐用于生产环境

```
root@ubuntu:/var/log# sysctl -w vm.overcommit_memory=2
```

跟 OOM 相关的配置还有 `/proc/sys/vm/overcommit_memory`，`man proc` 的解释如下：

```
This file contains the kernel virtual memory accounting mode.  Values are:

	0: heuristic overcommit (this is the default)
	1: always overcommit, never check
	2: always check, never overcommit
```

- 0 代表如果当进程申请的虚拟内存远大于物理内存时，则触发 OOM (例如物理内存 8g，申请虚拟内存 24g)
- 1 代表无论申请多大的虚拟内存都允许，但当物理内存耗尽时，则触发 OOM
- 2 代表会有一个 `RAM * SWAP * 系数` 的额度，当这次申请的虚拟内存加上之前已经申请的虚拟内存超过了额度，则触发 OOM (系数可以通过 `cat /proc/sys/vm/overcommit_ratio` 查看)

---

### <font color=#00b0f0>总结</font>

对于内存这些敏感且珍贵的系统资源，除了在分配使用上面有很多的保护机制之外，在一些特殊情况下同样有像 OOM 这样的方法去保证这方面的健壮性。同时通过
对 `oom_badness` 函数的简单了解，也可以看到实现上是用了很朴实的方法，并没有什么很玄乎的技巧，在个人的印象中，内核这种朴实无华的实现方式并不少，在狂秀语法糖的今天，值得我们深思
