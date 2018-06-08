### 概述

时至今日，CPU 主频早已突破 3GHz，内存也步入 DDR4 时代，磁盘在容量上越来越大，但是机械磁盘读写性能性能的增长却远远跟不上 CPU 和内存，这是由于机械磁盘的物理结构的限制 (可以参考 [直观图](https://github.com/hsxhr-10/blog/blob/master/Linux/%E3%80%90%E7%A3%81%E7%9B%98%20IO%E3%80%91--%20%E6%80%A7%E8%83%BD%E6%8C%87%E6%A0%87(%E8%A3%B8%E7%9B%98).md))，这也让机械磁盘 I/O 成了计算机性能提高的一个瓶颈。虽然有 SSD 磁盘的出现，读写 I/O 的性能比机械磁盘翻了 2 个数量级，但其较高的价格使得无法短时间内替代机械磁盘。

同时，对于系统管理员来说，相比 CPU 和内存的优化，磁盘 I/O 的性能优化选择多很多，但是，这些优化都是建立在一定的知识储备上的，如果没有这些储备就直接跳到优化这一步，就无法做到结合自己的实际情况，只能生搬硬套或者 “凭感觉” 去修改参数，这样往往会没效果甚至有反效果。因此，我觉得很有必要从块设备子系统的分层模型出发，逐层击破，弄明白各层的作用和联系，这样在优化时才有方向感。

---

### 七层模型

一个磁盘系统的分层模型如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/%E7%A3%81%E7%9B%98%E5%88%86%E5%B1%82%E6%A8%A1%E5%9E%8B.png)

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/%E5%9D%97%E8%AE%BE%E5%A4%87%E5%88%86%E5%B1%82%E5%9B%BE2.jpg)

下面简单介绍每一层的意义：

- **VFS Layer**：虚拟文件系统层。为一个抽象层，为上层用户空间屏蔽下层实际文件系统的细节，提供一套统一的文件系统操作接口，相当于文件系统的管理者。使得用户空间只需调用同一个 read() 函数，就可以即对 Ext3 文件系统读取，也可以对 NFS 文件系统读取 (可优化程度较低)。正是 VFS 的存在使得 Linux 可以兼容多文件系统，也让 “一切皆文件” 的理念得已实现
- **Page Cache Layer**：页缓存层。提供预读和回写机制，极大提高了磁盘的 I/O 性能
- **FS Layer**：文件系统层。具体的文件系统，跟 VFS 存在映射关系
- **Generic Block Layer**：通用块层。负责为上层提供一个抽象层，屏蔽掉下层具体的块设备类型，Generic Block Layer 和 Block Device Layer 的之间就类似 VFS 和 FS 的关系。由于上三层对于数据的 I/O 是以块或者页作为数据的单位，下三层对数据的 I/O 则是以扇区作为数据的单位，通用块层就做了这种转换操作，让上三层和下三层能顺利沟通，真正的面向硬件设备的 I/O 请求也是从该层发出
- **I/O Scheduler Layer**：I/O 调度层。提供不同的调度算法，并根据算法，合并可以合并的 I/O 请求，对请求重新排序，向 Block Device Drive Layer 发送 I/O 请求
- **Block Device Drive Layer**：块设备驱动层。磁盘设备的驱动程序，负责和磁盘控制器打交道
- **Block Device Layer**：块设备层。磁盘控制器，磁盘设备等硬件层

> 优化的性价比：Block Device Layer > Page Cache Layer > FS Layer > I/O Scheduler Layer > (VFS Layer, Generic Block Layer, Block Device Drive Layer)
