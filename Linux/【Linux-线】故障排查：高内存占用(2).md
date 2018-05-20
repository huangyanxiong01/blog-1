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

在[【Linux-线】故障排查：高内存占用(1).md](https://github.com/oooooxooooo/blog/blob/master/Linux/%E3%80%90Linux-%E7%BA%BF%E3%80%91%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5%EF%BC%9A%E9%AB%98%E5%86%85%E5%AD%98%E5%8D%A0%E7%94%A8(1).md)
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

虽然 OOM 是内核空间的事情，但是我们也可以在用户空间去做一些修改和配置。对于 OOM 有 4 种应对处理方式：

- 默认方式：让内核去 Kill 掉内存占用最多的进程
- 自动重启：当有进程触发 OOM 时，不采取默认方式，而是系统自动重启，通过 `vm.panic_on_oom` 和 `kernel.panic` 两个内核参数去控制。个人感觉这种随便重启的方式非常的不好，所以不做谈论
- 调整 `oom_score_adj` 参数：内核在执行 OOM Killer 时是根据 `points` 和 `oom_score_adj` 的总和去做判断的，总和越大的越容易被 kill 掉。(参考 [linux/mm/oom_kill.c](https://github.com/torvalds/linux/blob/master/mm/oom_kill.c) 的 `oom_badness` 函数)。

```
# oom_badness 函数关于两个关键参数的截取

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

其中，`points` 是进程所占用的内存大小，而 `oom_score_adj` 是内核留给用户空间做调整的参数。比如 `points` 数值相差不多的两个进程 A 和 B，如果我不想让 B 那么容易被 OOM Killer 处理掉，我就可以把 B 的 `oom_score_adj` 参数设置得更小。例如我想让 dockerd 的服务不那么容易被 kill：

```
# 通过 ps 找到 PID
root@ubuntu:/var/log# ps aux | grep dockerd | grep -v color
root       956  0.1  1.9 372996 19844 ?        Ssl  May16   9:17 /usr/bin/dockerd --raw-logs

# 通过 /proc 找到进程的 oom_score_adj 值
root@ubuntu:/var/log# cat /proc/956/oom_score_adj
-500

# 改写 oom_score_adj 值
root@ubuntu:/var/log# echo > -1000 /proc/956/oom_score_adj
```

- 关闭 OOM Killer：非常不推荐用于生产环境

```
root@ubuntu:/var/log# sysctl -w vm.overcommit_memory=2
```








