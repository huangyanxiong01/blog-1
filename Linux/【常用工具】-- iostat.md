### <font color=#00b0f0>简介</font>

`iostat` 是 Linux 下最基本的 I/O 设备性能工具，它提供的信息比较丰富且个别字段的意义很容易混淆，本文重点讨论那些模糊不清的字段真正的意义和搞清楚 `iostat` 能做什么不能做什么。

---

### <font color=#00b0f0>运行环境</font>

```
# uname -a
Linux ubuntu 3.16.0-30-generic #40~14.04.1-Ubuntu SMP Thu Jan 15 17:43:14 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux

# python2 --version
Python 2.7.9

# cat /etc/*-release
DISTRIB_DESCRIPTION="Ubuntu 14.04.2 LTS"
```

---

### <font color=#00b0f0>字段的意义</font>

`iostat` 的输出分两部分，第一部分是 CPU 的报告，第二部分是 I/O 设备的报告，下面重点看第二部分

```
root@ubuntu:/opt# iostat -xmtp 3
Linux 3.16.0-30-generic (ubuntu) 	05/31/2018 	_x86_64_	(2 CPU)

05/31/2018 10:04:45 AM
avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           4.85    0.00   27.47   15.98    0.00   51.71

Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
sda               0.00     2.00    0.00 7135.00     0.00    27.88     8.00     0.80    0.11    0.00    0.11   0.11  79.60
sda1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sda2              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sda5              0.00     2.00    0.00 7134.67     0.00    27.88     8.00     0.80    0.11    0.00    0.11   0.11  79.60
dm-0              0.00     0.00    0.00 7136.67     0.00    27.88     8.00     0.78    0.11    0.00    0.11   0.11  77.87
dm-1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00

...
```

- Device：对应 `/dev` 目录下的的设备 (加了 `-p` 参数会显示设备的分区，如 `sda1`)
- rrqm/s：每秒合并的读 I/O 个数，当多个 I/O 读取相邻的数据块时，这些读 I/O 将会被合并成一个，提高读取效率，通过该参数也可以猜测随机 I/O 和顺序 I/O 的比例
- wrqm/s：每秒合并的写 I/O 个数，当多个 I/O 写入相邻的数据块时，这些写 I/O 将会被合并成一个，提高写入效率，通过该参数也可以猜测随机 I/O 和顺序 I/O 的比例
- r/s：每秒的读 I/O 个数
- w/s：每秒的写 I/O 个数
- rMB/s：每秒读取的字节数 (加了 `-m` 参数，所以显示的是 MB/s，默认 KB/s)
- wMB/s：每秒写入的字节数 (加了 `-m` 参数，所以显示的是 MB/s，默认 KB/s)
- avgrq-sz：每个 I/O 的平均扇区个数
- avgqu-sz：未完成的 I/O 个数 (包括内核队列等待未完成和设备处理未完成)
- await：每个 I/O 平均花费的时间 (包括内核队列时间等待和设备处理时间)
- r_await：每个读 I/O 平均花费的时间 (包括内核队列时间等待和设备处理时间)
- w_await：每个写 I/O 平均花费的时间 (包括内核队列时间等待和设备处理时间)
- svctm：已废弃的字段，参考 man 手册 `Warning! Do not trust this field any more.  This  field  will be removed in a future sysstat version.`
- util：该设备有 I/O 的时间比 (重点是有没有 I/O，不考虑有多少 I/O)

> `iostat` 能让我们了解到有没有 I/O；随机和顺序 I/O 的比例；读写 I/O 的比例；读写 I/O 的数据量大小；未完成的 I/O 个数；大概的 I/O 时间等，通过这些信息我们可以对设备的现状作出一个初步的评估

---

### <font color=#00b0f0>正确理解 iostat</font>

#### 问题 1：await/r_await/w_await 很大就代表硬件设备有问题？

**一个 I/O (无论读写) 所花费的时间 = 内核队列排队时间 + 设备处理时间**，而 `iostat` 是基于 proc 文件系统中的 `/proc/diskstats` 所提供的采集信息进行统计的，但是**由于 `/proc/diskstats` 并没有将内核队列排队时间和设备处理时间分开处理**，因此当 `iostat` 的 await/r_await/w_await 字段的值偏高时，是无法分辨出到底是内核队列排队花太多时间，还是设备处理花太多时间。await/r_await/w_await 这几个字段更多是作为一个参考值，如果想更进一步确定是内核的 I/O Scheduler 出了问题还是硬件设备出了问题，可以通过像 blktrace 这样的工具去解决问题。

#### 问题 2：await 多大才算有问题？

对于 SSD 磁盘来说，一般是 2ms 以下；对于机械磁盘，一般 9ms 以下。[参考](http://cseweb.ucsd.edu/classes/wi01/cse102/sol2.pdf)

#### 问题 3：util 很大就代表设备已经处于饱和？

前面已经提到 util 代表的是该设备有 I/O 的时间比，只考虑有没有 I/O，而不管到底有多少 I/O。

举个例子，有 10 个 I/O，磁盘处理每个 I/O 需要 0.1s。当应用串行地发送 10 个 I/O 请求到设备，则在 1s 内，设备的 util 值就是 100；假设设备具有并行的处理能力，能同时处理 10 个请求，应用同时发送 10 个 I/O 请求到设备，则在 1s 内，设备的 util 就是 10。

因此，util 并不能作为判断 I/O 设备是否已经饱和的依据，只能作为参考，同时通过 util 能肯定的只是设备是否有 I/O 而已。

#### 问题 4：谁负责请求合并？

有时候会发现不通设备的 rrqm/s 之间或 wrqm/s 之间会相差比较大，通过 `cat /sys/block/设备名/queue/scheduler` 可以

