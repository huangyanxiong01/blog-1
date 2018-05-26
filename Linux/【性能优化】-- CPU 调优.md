### <font color=#00b0f0>运行环境</font>

```
# uname -a
Linux ubuntu 3.16.0-30-generic #40~14.04.1-Ubuntu SMP Thu Jan 15 17:43:14 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux

# python2 --version
Python 2.7.9

# cat /etc/*-release
DISTRIB_DESCRIPTION="Ubuntu 14.04.2 LTS"

# 2G 内存
# CPU：2核
```

### <font color=#00b0f0>调优工具</font>

想要快速确定一个问题是 CPU 造成的，其实不是一件很容易的事情，因为 CPU 需要跟不同的子系统互相通信，所以很多时候表现出来的只是表象，背后真相可能是其他子系统造成的问题。比如当 CPU 的利用率很高时，有可能是真的在高速地处理者任务，也有可能是因为某个系统事件阻塞在那里；或者在增加了 CPU 数量之后，发现进程服务的 CPU 占用还是非常高。

除了 [【性能优化】-- top](https://github.com/hsxhr-10/blog/blob/master/Linux/%E3%80%90%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%E3%80%91--%20top.md) 中提到的 `top`，下面还会介绍一些其他非常好用的 CPU 调优工具

#### vmstat

```
root@ubuntu:/proc/28941# vmstat 1 
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 0  0      0 270968 121320 443424    0    0     1    82   61   33  0  0 99  0  0
 0  0      0 270984 121320 443424    0    0     0     0   83  188  1  1 99  0  0
 0  0      0 270984 121320 443424    0    0     0     0   56  113  0  0 100  0  0
 
 ...
```

- **r** 代表正在运行的进程数。由此可以大概了解 CPU 的繁忙程度
- **b** 代表阻塞的进程数。当这个值持续大于 0 时，可以推测 CPU 正在被某个进程阻塞，该进程的 CPU 占用率通常非常高，此时可以将排查方向转向该进程，看是否进程代码的编程模型出了问题，抑或是进程所依赖的其他系统出了问题
- **swpd** 代表磁盘 swap 的使用量。当这个值偏大时，频繁的磁盘 swap 会造成很大的 CPU 负担，此时可以将排查方向转向内存不足问题上
- **si/so** 代表 CPU 每秒从磁盘读/写入虚拟内存的大小。当这个两个值持续偏大时，排场方向同上
- **bi/bo** 代表块设备每秒读/写的块数量。当这个两个值持续偏大时，证明磁盘设备非常繁忙，可能会造成 `wa` 指标升高
- **in** 代表中断次数
- **cs** 代表上下文切换次数
- **us/sy** 代表用户进程和系统进程所占的 CPU 事件

1. 当 `r` 的值很大，`us+sy` 大于 80%，其他的指标正常时，可以初步推断为 CPU 资源不足，通过升级或者增加 CPU 资源解决。
2. 当 `swpd` 和 `si/so` 持续偏高时，可以初步推断为内存资源问题，通过排查是否存在[内存泄漏](https://github.com/hsxhr-10/blog/blob/master/Linux/%E3%80%90%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5%E3%80%91--%20%E9%AB%98%E5%86%85%E5%AD%98%E5%8D%A0%E7%94%A8(1).md)或者增加内存解决。
3. 当 `bi/bo` 和 `wa` 持续偏高时，可以推断为磁盘资源问题，通过排查高磁盘 IO 进程或更换 SSD 解决。

> vmstat 关注的是**是否单纯因为 CPU 资源不足**；**是否因为其他子系统引发的 CPU 性能问题**

#### mpstat

```
root@ubuntu:/proc/28941# mpstat -P ALL 1
Linux 3.16.0-30-generic (ubuntu) 	05/26/2018 	_x86_64_	(2 CPU)

03:44:17 AM  CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
03:44:18 AM  all    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
03:44:18 AM    0    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
03:44:18 AM    1    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00

...
```

如果是多核的情况下，`mpstat` 命令能查看每个核心的情况。重点看到 `%irq` 字段，该字段代表了某一个核心被硬中断所占用的时间，当某一个核心的 `%irq` 值非常大，而其他核心的值却很小时，需要警惕是否硬中断负债出现了问题。

所谓硬中断指的是 CPU 和硬件的一种沟通方式，因为每个硬件 (磁盘、网卡) 都需要让 CPU 及时知道自己这边发生了什么事，这样 CPU 可能就会放下正在处理的任务进而去处理比较急的事件，像这种硬件主动干扰/通知 CPU 的行为就是硬中断。

默认情况下，系统提供 irqbalance 服务进行硬中断的分配，并且效果不错，用户无需关心这个问题。但是在一些特殊的应用场景下，比如对于文件服务器、高流量 Web 服务器这样的应用来说，当发现多个网卡的请求都集中在同一个 CPU 时，通过把不同的网卡硬中断请求均衡绑定到不同的 CPU 上将会减轻某个 CPU 的负担，提高多个 CPU 整体处理中断的能力。具体绑定方法可以参考[这里](https://www.cnblogs.com/bamanzi/p/linux-irq-and-cpu-affinity.html)。

> mpstat 关注的是**硬中断负载均衡**

#### taskset

该命令将绑定进程到指定的 CPU 上，这种人为的绑定可以使得进程在多核新的使用上比较均衡

```
# 默认情况下，进程 31647 在 CPU0 和 CPU1 之间切换运行

...

# 绑定进程 31647 在 CPU0 上运行
root@ubuntu:/proc/28941# taskset -cp 0 31647
pid 31647's current affinity list: 1
pid 31647's new affinity list: 0
root@ubuntu:/proc/28941#

# top 可以看到 CPU0 很忙，CPU1 很闲
top - 04:36:11 up 3 days,  5:33,  4 users,  load average: 1.00, 0.80, 0.42
Tasks: 175 total,   3 running, 172 sleeping,   0 stopped,   0 zombie
%Cpu0  :  9.8 us, 59.0 sy,  0.0 ni,  0.0 id, 31.3 wa,  0.0 hi,  0.0 si,  0.0 st
%Cpu1  :  0.8 us,  0.8 sy,  0.0 ni, 97.5 id,  0.0 wa,  0.0 hi,  0.8 si,  0.0 st
KiB Mem:   1014068 total,   747784 used,   266284 free,   122772 buffers
KiB Swap:        0 total,        0 used,        0 free.   443588 cached Mem

...

# 绑定进程 31647 在 CPU1 上运行
root@ubuntu:/proc/28941# taskset -cp 1 31647
pid 31647's current affinity list: 0
pid 31647's new affinity list: 1
root@ubuntu:/proc/28941#

# top 可以看到 CPU1 很忙，CPU0 很闲
top - 04:38:05 up 3 days,  5:35,  4 users,  load average: 1.00, 0.86, 0.49
Tasks: 175 total,   4 running, 171 sleeping,   0 stopped,   0 zombie
%Cpu0  :  0.7 us,  0.3 sy,  0.0 ni, 98.6 id,  0.0 wa,  0.0 hi,  0.3 si,  0.0 st
%Cpu1  : 13.1 us, 55.6 sy,  0.0 ni,  0.0 id, 19.8 wa,  0.0 hi, 11.5 si,  0.0 st
KiB Mem:   1014068 total,   747564 used,   266504 free,   122880 buffers
KiB Swap:        0 total,        0 used,        0 free.   443596 cached Mem

...

# 绑定进程 31647 在 CPU0 和 CPU1 之间切换运行
root@ubuntu:/proc/28941# taskset -cp 0-1 31647
pid 31716's current affinity list: 1
pid 31716's new affinity list: 0,1

# top 可以看到 CPU1 和 CPU0 差不多忙
top - 04:41:18 up 3 days,  5:38,  4 users,  load average: 0.83, 0.79, 0.53
Tasks: 176 total,   3 running, 173 sleeping,   0 stopped,   0 zombie
%Cpu0  :  4.7 us, 24.7 sy,  0.0 ni, 49.5 id, 21.1 wa,  0.0 hi,  0.0 si,  0.0 st
%Cpu1  :  5.0 us, 26.7 sy,  0.0 ni, 43.3 id, 10.0 wa,  0.0 hi, 15.0 si,  0.0 st
KiB Mem:   1014068 total,   748148 used,   265920 free,   123036 buffers
KiB Swap:        0 total,        0 used,        0 free.   443596 cached Mem

...
```

> taskset 关注的是**多核芯利用率**

#### 充分了解你的应用

基于运行的应用，确认你的应用是否能高效的利用多处理器。来决定是否应该使用更强劲的CPU而不是更多的CPU。例如，单线程应用，会从更快的CPU中受益，增加值CPU个数也没用。

根据所运行的应用类型，确定应用是否能够充分利用多核芯的 CPU 来选择是升级更加强劲的 CPU 还是加更多的 CPU。比如，单进程单线程的应用会从更强劲的 CPU 中获益，增加 CPU 个数几乎没用；而多进程则是增加 CPU 和数来得更加实惠。

#### 其他方面

- 确保没有运行不必要的进程
- 对于某些非关键的进程，可以通过 `renice` 命令去修改其优先级
- 使用程序自带的调整 CPU 的功能，如 Nginx 可以通过 `work_cpu_affinity` 参数去为每个子进程绑定指定的 CPU
- 尽量使用最新的驱动
