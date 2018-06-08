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
