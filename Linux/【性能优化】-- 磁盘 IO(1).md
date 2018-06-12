### 概述

本文根据磁盘 IO 七层模型作为指导来进行性能优化，上图：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/块设备分层图2.jpg)

> 注意，这里的优化不会涉及修改内核代码

---

### 优化方法

#### Block Device Driver Layer / Generic Block Layer

这两层的
