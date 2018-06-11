![](https://raw.githubusercontent.com/hsxhr-10/picture/master/FS%20Layer.png)

---

- 硬盘物理扇区与文件系统文件之间的对应关系
- 文件系统相关命令
- 常见文件系统

---

### 概述

文件系统的主要作用是规定好数据是以什么格式存放在物理设备上。通俗点说就是有一块磁盘，但是数据在磁盘上面是如何组织的，这事就由文件系统来管。

#### ext4 磁盘格式

以 ext4 文件系统为例，ext4 文件系统对磁盘数据的组织格式是由一个 `boot block` 和多个 `block group` 组成的，如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/ext4-磁盘格式1.png)

其中，每个 `block group` 又是由 `super block`, `group descriptors`, `data bitmap`, `inode bitmap`, `inode table`, `data blocks` 组成 (并且 `super block` 和 `inode table` 会映射到内存中的 VFS) 如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/ext4-磁盘格式2.png)

- **super block**：记录文件系统的信息 (内核只会用到第一个，其他的都是冗余)
- **group descriptors**：记录所有的 block group 的信息 (内核只会用到第一个，其他的都是冗余)
- **data bitmap**：记录 data blocks 的使用情况
- **inode bitmap**：记录 inode table 的使用情况
- **inode table**：记录该组所有文件的元数据
- **data blocks**：记录该组所有实际数据

---

### 文件路径、block、inode、sector

*下面说的文件路径默认是绝对路径*

从上面的介绍我们已经知道了一个文件，比如 `/usr/lib/libpq.a` 是以何种格式组织于磁盘中的。理论总是抽象的，下面来实践下，实际看下一个文件在各层的表示方式和相互转换。

- 文件路径：用户空间操作数据的基本单元
- block：VFS, FS 操作数据的基本单元
- inode：联系着用户空间和 VFS；VFS 和 FS
- sector：物理设备操作数据的基本单元

文件在用户空间通常都是以文件路径的形式来表示，这也是我们最熟悉的一种方式；在 VFS 和 FS 中，文件通常是以 block (数据块) 的形式来表示，inode 则是联系用户空间和 VFS, VFS 和 FS；而在物理设备层面上，文件则是由于 sector (扇区) 来表示。

#### 例子

根据文件路径查找 inode

```
root@120:~# ls -i /usr/lib/libpq.a
3277421 /usr/lib/libpq.a

# 3277421 就是文件 /usr/lib/libpq.a 的 inode number
```




