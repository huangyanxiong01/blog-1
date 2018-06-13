### 概述

本文根据磁盘 IO 七层模型作为指导来进行性能优化，上图：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/块设备分层图2.jpg)

> 注意，这里的优化不会涉及修改内核代码

---

### 优化方法

#### Block Device Layer

根据应用场景，如果对响应延迟、随机 IOPS 等性能指标要求比较高的场景，能用 SSD 的就不要用 HDD；相反，对于一些延迟要求较低或者吞吐量优先级最高的场景，比如  Hadoop 离线计算之类的，就优先用 HDD 来撑大吞吐量，而且钱方面的成本也低得多。同时，在选购完块设备后，需要用工具去测试块设备的 IOPS, 吞吐量, 延迟等性能指标，可以参考 [这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【磁盘%20IO】--%20性能测试(Block%20Device%20Layer).md)。

#### Block Device Driver Layer / Generic Block Layer / VFS Layer

这 3 层的可操作程度相对来说是最低的，性价比最高的做法就是确保所安装的内核是信得过的，版本不要过低并且应该是 LTS 版本。

#### I/O Scheduler Layer

1. 根据 [I/O 调度器的选择](https://github.com/hsxhr-10/blog/blob/master/Linux/【磁盘%20IO】--%20IO%20Scheduler%20Layer.md#io-调度器的选择)

- Web 服务器，数据库服务 => Deadline
- 非 SATA/SAS 接口的固态磁盘 => NOOP
- 万金油，特别适用于桌面系统，多媒体应用服务 => CFQ

```
# 查看
root@120:~# cat /sys/block/sda/queue/scheduler 
noop [deadline] cfq

# 方括号括着表示该块设备当前的 I/O Scheduler 是 deadline

# 修改成 cfq
root@120:~# echo cfq > /sys/block/sda/queue/scheduler
root@120:~# cat /sys/block/sda/queue/scheduler 
noop deadline [cfq] 
```

2. 调整队列长度

理论上，对于小文件，增大队列会提升性能；对于大文件，减小队列会提升性能。但是应该根据实际情况，边修改变测试，直到有一个能满足实际的值。

```
# 查看
root@120:~# cat /sys/block/sda/queue/nr_requests
128

# 修改
root@120:~# echo 256 > /sys/block/sda/queue/nr_requests
```

#### FS Layer

1. 根据实际场景，选择合适的文件系统，参考 [这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【磁盘%20IO】--%20FS%20Layer.md#2-选择对照表)，总的来说，选 ext4 一般是不会出大错的。

2. 根据 [这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【磁盘%20IO】--%20FS%20Layer.md) 我们知道文件系统维护着元数据和实际数据两部分的数据，实际数据是不可能减少了，但是可以通过减少非必要的元数据来提升性能。对于很多场景，atime (文件的最后访问时间) 是非必须的，因此可以减少对 atime 的维护。

```
# 方法 1 挂载时指定
root@120:~# mount /dev/sda1 / -o defaults,noatime

# 方法 2 修改 /etc/fstab
root@120:~# vim /etc/fstab

/dev/sda1 / ext4 defaults,noatime 1 2
```

3. 通过增大 block size 和 inode size 来减少磁盘寻道时间和元数据操作时间，但是需要注意的是 block size 不能大于 page size。

```
# 查看 block size 和 inode size
root@120:/usr/lib# debugfs /dev/dm-0
debugfs 1.42.9 (4-Feb-2014)
debugfs:  show_super_stats
Filesystem volume name:   <none>
...
Block size:               1024
...
Inode size:               256
...

# 查看 page size
root@120:~# getconf PAGE_SIZE
4096

# 修改 block size 和 inode size
root@120:~# mkfs.ext4 -b 4096 -i 512 /dev/dm-0
```

4. 修改日志模式

不建议关闭日志功能，建议修改日志模式。journal 元数据和数据都记录；ordered 只记录元数据；writeback 利用缓存的方式记录元数据。可靠性方面：journal > ordered (默认) > writeback，性能方面则相反。

```
# 挂载时指定日志模式
root@120:~# mount /dev/sda1 / -o defaults,noatime,data=writeback
```

#### Page Cache Layer

1. 在合理的范围内，尽量选购大容量的内存。因为 Page Cache Layer 在读写缓冲方面的性能都严重依赖于内存的容量大小。

> 预读和回写的相关知识可以参考 [这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【磁盘%20IO】--%20Page%20Cache%20Layer.md#预读和回写)

2. 回写

2.1. `/proc/sys/vm/dirty_ratio` 这个参数控制着 Page Cache Layer 的写缓冲区大小，单位是百分比。代表当写缓冲区占物理内存的多少时，开始向磁盘写数据。增大该值可以极大提高写性能，当然也要结合场景，当需要实时写入磁盘时，就需要调小该值。默认值 10。

```
root@120:~# cat /proc/sys/vm/dirty_ratio
20
```

2.2. `/proc/sys/vm/dirty_expire_centisecs` 这个参数控制着写缓冲区中的数据多 “旧” 之后，就要被写入磁盘，单位是 1/100秒。调大该值也可以大大提升写性能。默认值 3000。

```
root@120:~# cat /proc/sys/vm/dirty_expire_centisecs
3000
```

2.3. `/proc/sys/vm/dirty_background_ratio` 这个参数和 1.1. 中的 `/proc/sys/vm/dirty_ratio` 基本一致，建议这两个参数取值一致。默认值 10。

```
root@120:~# cat /proc/sys/vm/dirty_background_ratio
20
```

2.4. `/proc/sys/vm/dirty_writeback_centisecs` 这个参数控制着脏数据刷新进程 pdflush 的运行间隔，单位是 1/100 秒。调大该值也可以适当提升写性能。

3. 预读

在非频繁的小文件随机 I/O 情况下，比如一些要求大吞吐量的业务场景，调大预读可以提高读性能。当然如果预读失败，可能反而会降低性能。

```
# 查看设备的预读大小，单位 Byte
root@120:~# blockdev --report
RO    RA   SSZ   BSZ   StartSec            Size   Device
rw   256   512  1024       2048       254803968   /dev/sda1

# RA 表示预读，可以看到预读大小为 256 Byte

# 修改
root@120:~# blockdev --setra 512 /dev/sda1
root@120:~# blockdev --report
RO    RA   SSZ   BSZ   StartSec            Size   Device
rw   512   512  1024       2048       254803968   /dev/sda1
```

4. swappiness

调小 swappiness 的值，减少交换操作导致的性能急剧下降。默认值 60。

```
# 查看
root@120:~# cat /proc/sys/vm/swappiness 
60

# 修改
root@120:~# echo 1 > /proc/sys/vm/swappiness
```

---

### 总结

#### 性能优化之前一定要搞清楚场景

- 从性能指标方面：随机 IOPS 要求? 吞吐量要求? 延迟要求?
- 从操作文件大小方面：偏重操作小文件？偏重操作大文件？
- 从读写比例方面：多读少写？多写少读？
- 从数据实时性方面：数据是否需要实时落盘？
- 从数据可靠性方面：是否允许丢失少量数据？

#### 关于 7 层优化

千万不要觉得 “换个磁盘/加内存” 这种解决方案是没技术含量的，因为如果底层的物理设备性能跟不上，上层再怎么优化其实效果也甚微，试想下物理内存本身就不够了，怎么通过调整内核参数加大写缓冲区？总的来说，选择质量好的 (贵的) 物理磁盘，在合理范围内选择更大的内存，保证系统内核的可靠性，根据业务场景选择适合的文件系统，能做到这些，已经可以很好地确保磁盘 I/O 子系统的整体性能了。在此基础上，再根据实际需要进行适当的参数调优即可。
