![](https://raw.githubusercontent.com/hsxhr-10/picture/master/I%3AO%20Scheduler%20Layer.png)

---

### 概述

I/O Scheduler Layer 处于 Generic Block Layer 和 Block Device Driver 之间。它的主要功能有两个，1 是合并相邻扇区的 I/O 请求，2 是对 I/O 请求进行重新排序并调度。

I/O Scheduler Layer 接收上层请求，并尝试合并相邻的请求，减少请求的数量，在一定程度上提高了性能和增大了吞吐量。我们可以通过 `iostat` 命令查看被合并的 I/O，结果中 `rrqm/s` 表示每秒合并的读 I/O 个数，`wrqm/s` 表示每秒合并的写 I/O 个数。如下：

```
root@ubuntu:/proc/sys/vm# iostat -xmtp 1
Linux 3.16.0-30-generic (120.78.66.191) 	06/07/2018 	_x86_64_	(2 CPU)

06/07/2018 06:09:16 PM
avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           0.22    0.00    0.14    0.10    0.00   99.54

Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
sda               0.01     5.78   24.25    1.05     0.10     0.10    15.91     0.11    4.54    0.05  108.02   0.09   0.24
sda1              0.01     0.00    0.00    0.00     0.00     0.00    54.77     0.00    0.23    0.23    0.44   0.19   0.00
sda2              0.00     0.00    0.00    0.00     0.00     0.00     2.00     0.00    0.00    0.00    0.00   0.00   0.00
sda5              0.00     5.78   24.25    0.54     0.10     0.10    16.24     0.11    4.64    0.05  210.10   0.09   0.23
dm-0              0.00     0.00   24.25    6.80     0.10     0.10    12.97     2.65   85.28    0.05  389.32   0.08   0.24
dm-1              0.00     0.00    0.00    0.00     0.00     0.00     8.00     0.00    0.43    0.43    0.00   0.15   0.00
```

假设没有 I/O Scheduler Layer，上层的 I/O 请求就会直接落到物理设备上，那么物理设备的性能肯定是不能接受的。因此，I/O Scheduler Layer 提供了几种 I/O 调度算法，对请求进行合并，重新规划请求的顺序，并通过队列将请求缓存起来，在算法认为适当的时机再发送合适的 I/O 请求到下层。

### 3 种调度算法

这里列举最常见的 3 种。

**CFQ**

CFQ 算法为每个进程分配两个资源：调度队列和时间片。调度队列会对进程的 I/O 请求进行缓存，每个队列有不同的优先级。时间片指的是分配给该进程的 I/O 服务时间。CFQ 算法会对 I/O 请求进行合并操作和重新排序操作。

CFQ 的目的是通过控制优先级、时间片等因素，最终让各个队列尽可能公平地使用下层的 I/O 资源。

**Deadline**

Deadline 算法维护两个调度队列，一个读队列，一个写队列。

**NOOP**
