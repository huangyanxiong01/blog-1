![](https://raw.githubusercontent.com/hsxhr-10/picture/master/FS%20Layer.png)

---

### ext4 磁盘格式

文件系统的主要作用是规定好数据是以什么格式存放在物理设备上。通俗点说就是有一块磁盘，但是数据在磁盘上面是如何组织的，这事就由文件系统来管。文件系统的种类很多，以 ext4 为例，ext4 文件系统对磁盘数据的组织格式是由一个 `boot block` 和多个 `block group` 组成的，如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/ext4-磁盘格式1.png)

其中，每个 `block group` 又是由 `super block`, `group descriptors`, `data bitmap`, `inode bitmap`, `inode table`, `data blocks` 组成 (并且 `super block` 和 `inode table` 会映射到内存中的 VFS) 如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/ext4-磁盘格式2.png)

- **super block**：记录文件系统的信息 (内核只会用到第一个，其他的都是冗余)
- **group descriptors**：记录所有的 block group 的信息 (内核只会用到第一个，其他的都是冗余)
- **data bitmap**：记录 data blocks 的使用情况
- **inode bitmap**：记录 inode table 的使用情况
- **inode table**：记录该组所有文件的元数据
- **data blocks**：记录该组所有实际数据

> 同一个文件的数据会尽量放到同一个 `block group` 中，减少磁盘的寻道时间

---

### 文件路径 和 block、inode、sector 之间的转换

*下面说的文件路径默认是绝对路径*

从上面的介绍我们已经知道了一个文件，比如 `/usr/lib/libpq.a` 是以何种格式组织于磁盘中的。理论总是抽象的，下面来实践下，实际看下一个文件在各层的表示方式和相互转换。

- 文件路径：用户空间操作数据的基本单元
- block：VFS, FS 操作数据的基本单元
- inode：联系着用户空间和 VFS；VFS 和 FS
- sector：物理设备操作数据的基本单元

文件在用户空间通常都是以文件路径的形式来表示，这也是我们最熟悉的一种方式；在 VFS 和 FS 中，文件通常是以 block (数据块) 的形式来表示，inode 则是联系用户空间和 VFS, VFS 和 FS；而在物理设备层面上，文件则是由于 sector (扇区) 来表示。

#### 例子

> 关系链条：文件路径 -- inode -- block -- sector

0. 预备操作

```
# 查看 sector 大小
root@120:~# fdisk -lu /dev/dm-0

Disk /dev/dm-0: 67.4 GB, 67385688064 bytes
255 heads, 63 sectors/track, 8192 cylinders, total 131612672 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
...

# 查看 block 大小
root@120:~# debugfs -R show_super_stats /dev/dm-0 | grep -i block
debugfs 1.42.9 (4-Feb-2014)
Block count:              16451584
Reserved block count:     822579
Free blocks:              8746256
First block:              0
Block size:               4096
Reserved GDT blocks:      1020
Blocks per group:         32768
Inode blocks per group:   512
Flex block group size:    16
Reserved blocks uid:      0 (user root)
Reserved blocks gid:      0 (group root)
Journal backup:           inode blocks
...
```

1. 从左往右

1.1. 根据文件路径查找 inode

```
root@120:~# ls -i /usr/lib/libpq.a
3277421 /usr/lib/libpq.a

# 3277421 就是文件的 inode number
```

1.2. 根据文件路径查找 block

```
root@120:/usr/lib# debugfs /dev/dm-0
debugfs 1.42.9 (4-Feb-2014)
debugfs:  stat /usr/lib/libpq.a

Inode: 3277421   Type: regular    Mode:  0644   Flags: 0x80000
Generation: 493211873    Version: 0x00000000:00000001
User:     0   Group:     0   Size: 323796
File ACL: 0    Directory ACL: 0
Links: 1   Blockcount: 640
Fragment:  Address: 0    Number: 0    Size: 0
 ctime: 0x59fbe0bb:02dc6c00 -- Fri Nov  3 11:21:31 2017
 atime: 0x5b010e2c:2638e590 -- Sun May 20 13:57:00 2018
 mtime: 0x59b1a800:00000000 -- Fri Sep  8 04:11:44 2017
crtime: 0x59fbe0ba:ea9a9800 -- Fri Nov  3 11:21:30 2017
Size of extra inode fields: 28
EXTENTS:
(0-79):15809024-15809103
(END)

# 重点看到 (0-79):15809024-15809103，(0-79) 就是文件的 block number，15809024-15809103 就是文件在 data blocks/块 中的位置。
# 15809024 是由 "(15809024 对应的 sector - 分区起始 sector) / 8 得到；15809103 是由 (15809103 对应的 sector - 分区起始 sector) / 8 得到，
# 之所以除 8 是因为 block size 4096B 和 sector size 512B 之间差了 4 倍。
```

1.3. 根据文件路径查找 sector

```
# 根据 1.2 知道 block 信息：(0-79):15809024-15809103，同时根据 block = (结束 sector - 分区起始 sector) / 8，
# 且文件所在分区的起始 sector 等于 2048，算得 sector 范围是：(2048-2680):126474240-126474872
```

2. 从右往左

2.1. 根据 inode 查找文件路径

```
root@120:/usr/lib# debugfs /dev/dm-0
debugfs 1.42.9 (4-Feb-2014)
debugfs:  ncheck 3277421
Inode	Pathname
3277421	/usr/lib/libpq.a
```

2.2. 根据 block 查找文件路径

```
# 先根据 block 查找 inode
root@120:/usr/lib# debugfs /dev/dm-0
debugfs 1.42.9 (4-Feb-2014)
debugfs:  icheck 15809024
Block	Inode number
15809024	3277421

# 转化成根据 inode 查找文件路径
```

2.3. 根据 sector 查找文件路径

```
# 假设有以下的日志信息
kernel: end_request: I/O error, dev sdb, sector 41913499

# 根据 sector 定位分区
root@120:~# fdisk -lu /dev/sdb
...
Device Boot      Start         End      Blocks   Id  System
/dev/sdb1              63    24595514    12297726   83  Linux
/dev/sdb2        24595515    41929649     8667067+  83  Linux

# 出错 sector 在分区 /dev/sdb2 中

# 根据公式：Blocks值 = （出错 sector – 分区起始 sector）/ 8，计算 sector 对应的 block，
# blocks=（41913499 – 分区起始 sector）/8 = （41913499 - 24595515）/8 = 2164748

# 转化成根据 block 查找文件路径
```

---

### 文件系统相关命令

- fdisk -lu
- mkfs.ext4
- mount
- umount
- dd
- debugfs

---

### 常见文件系统

