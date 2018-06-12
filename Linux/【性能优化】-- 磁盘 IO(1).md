### 概述

本文根据磁盘 IO 七层模型作为指导来进行性能优化，上图：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/块设备分层图2.jpg)

> 注意，这里的优化不会涉及修改内核代码

---

### 优化方法

#### Block Device Layer

根据应用场景，如果对响应延迟、随机 IOPS 等性能指标要求比较高的场景，能用 SSD 的就不要用 HDD；相反，对于一些延迟要求较低或者吞吐量优先级最高的场景，比如  Hadoop 离线计算之类的，就优先用 HDD 来撑大吞吐量，而且钱方面的成本也低得多。同时，在选购完块设备后，需要用工具去测试块设备的 IOPS, 吞吐量, 延迟等性能指标，可以参考[这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【磁盘%20IO】--%20性能测试(Block%20Device%20Layer).md)。

#### Block Device Driver Layer / Generic Block Layer / VFS Layer

这两层的可操作程度相对来说是最低的，性价比最高的做法就是确保所安装的内核是信得过的，版本不要过低并且应该是 LTS 版本。

#### 
