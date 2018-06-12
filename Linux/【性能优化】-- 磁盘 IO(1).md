### 概述

本文根据磁盘 IO 七层模型作为指导来进行性能优化，上图：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/块设备分层图2.jpg)

> 注意，这里的优化不会涉及修改内核代码

---

### 优化方法

#### Block Device Layer

根据应用场景，如果对响应延迟、随机 IOPS 等性能指标要求比较高的场景，能用 SSD 的就不要用 HDD；相反，对于一些延迟要求较低或者吞吐量优先级最高的场景，比如  Hadoop 离线计算之类的，就优先用 HDD 来撑大吞吐量，而且钱方面的成本也低得多。同时，在选购完块设备后，需要用工具去测试块设备的 IOPS, 吞吐量, 延迟等性能指标，可以参考[这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【磁盘%20IO】--%20性能测试(Block%20Device%20Layer).md)。

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

1. 根据实际场景，选择合适的文件系统，参考[这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【磁盘%20IO】--%20FS%20Layer.md#2-选择对照表)，总的来说，选 ext4 一般是不会出大错的。

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


1. 调整 VM 系统内核参数

1.1. `/proc/sys/vm/dirty_ratio` 这个参数控制着 Page Cache Layer 的写缓冲区大小，单位是百分比。代表当写缓冲区占物理内存的多少时，开始向磁盘写数据。增大该值可以极大提高磁盘 I/O 的写性能，当然也要结合场景，当需要实时写入磁盘时，就需要调小该值。

```
root@120:~# cat /proc/sys/vm/dirty_ratio
20
```

1.2. `/proc/sys/vm/dirty_expire_centisecs` 这个参数控制着写缓冲区中的数据多 “旧” 之后，就要被写入磁盘，单位是 1/100秒。调大该值也可以大大提升写性能。
















