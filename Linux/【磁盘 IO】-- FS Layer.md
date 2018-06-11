![](https://raw.githubusercontent.com/hsxhr-10/picture/master/FS%20Layer.png)

---

- 硬盘物理扇区与文件系统文件之间的对应关系
- 文件系统相关命令
- 常见文件系统

---

### 概述

问：什么是文件系统？答：文件系统是对一个存储设备上的数据和元数据进行组织的机制。通俗点说就是我有一块磁盘，但是数据在磁盘上面是如何组织存放的，就文件系统来管这事了。

#### ext4 磁盘格式

以 ext4 文件系统为例，ext4 文件系统对磁盘数据的组织格式是由一个 `boot block` 和多个 `block group` 组成的，如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/ext4-磁盘格式1.png)

其中，每个 `block group` 又是由 `super block`, `group descriptors`, `data bitmap`, `inode bitmap`, `inode table`, `data blocks` 组成 (并且 `super block` 和 `inode table` 会映射到内存中的 VFS) 如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/ext4-磁盘格式2.png)
