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

根据[I/O 调度器的选择](https://github.com/hsxhr-10/blog/blob/master/Linux/【磁盘%20IO】--%20IO%20Scheduler%20Layer.md#io-调度器的选择)

- Web 服务器，数据库服务 => Deadline
- 非 SATA/SAS 接口的固态磁盘 => NOOP
- 万金油，特别适用于桌面系统，多媒体应用服务 => CFQ

```
# 查看 I/O Scheduler
cat /sys/block/{DEVICE-NAME}/queue/scheduler
# 修改 I/O Scheduler
echo {SCHEDULER-NAME} > /sys/block/{DEVICE-NAME}/queue/scheduler

# 例子
root@120:~# cat /sys/block/sda/queue/scheduler 
noop [deadline] cfq

# 方括号括着表示该块设备当前的 I/O Scheduler 是 deadline

# 修改成 cfq
root@120:~# echo cfq > /sys/block/sda/queue/scheduler
root@120:~# cat /sys/block/sda/queue/scheduler 
noop deadline [cfq] 
```


