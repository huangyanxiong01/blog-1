### 概述

Linux 为了支持不同的文件系统，就需要一个抽象层将具体文件系统的细节屏蔽掉，只要文件系统的实现能遵循一定的规则，就能和这个抽象层顺利配合，并且抽象层对外提供统一的操作接口，让用户空间无论操作哪个文件系统都只需要作出一样的操作，这个抽象层就是虚拟文件系统 --- VFS。

---

### VFS 支持的文件系统类型

- 基于磁盘的文件系统
  - Linux：Ext2, Ext3, Ext4, ReiserFS 等
  - Unix 文件系统的变种：sysv, UFS
  - 微软文件系统：MS-DOS, VFAT
  - ISO9660 CD-ROM 文件系统和 DVD 文件系统
- 基于网络的文件系统
  - NFS
- 特殊文件系统
  - /proc

> 第一二种都是管理块设备的文件系统，第三种则不是

---

### VFS 4 大组成对象

- **superblock**：超级块。表示某个加载的文件系统
- **inode**：索引节点。表示某个文件
- **dentry**：目录项。表示路径的一个组成部分
- **file**：文件对象。表示被某个进程打开的一个文件

> 这些对象都是存放于内存当中

#### superblock

superblock 用于存放文件系统的信息，管理 VFS 和文件系统的映射关系 (包括 superblock 映射、inode 映射等)。这个对象对应着文件系统中的 superblock，但是文件系统中的 superblock 是存放于磁盘当中。

superblock 的成员变量由结构 `struct super_block` 表示，比较常见的有：

- `s_type`：文件系统类型
- `s_dev`：设备标识符
- `s_op`：操作函数

superblock 的操作函数由 `super_operations` 结构体表示，比较常见的有：

- alloc_inode(sb)：初始化一个新的 inode
- destroy_inode(inode)：释放 inode
- read_inode(inode)：读文件系统中的 inode 内容，并写入内存中对应 VFS 的 inode 中
- write_inode(inode, wait)：将 VFS 中 inode 写入文件系统中的 inode
- sync_fs(sb, wait)：同步 VFS 和文件系统中的数据

这些函数的具体实现由文件系统提供，VFS 只提供接口名，这就体现了抽象层的作用了。上述结构体都定义在文件 `include/linux/fs.h` 中。

#### inode

一个 inode 对象对应着一个文件/目录，inode 存放着内核操作文件/目录时所需的一切信息，形象点来说就是执行 `ls -l` 时的信息都是 inode 提供的。

这个对象对应着文件系统中的 inode，但是文件系统中的 inode 是存放于磁盘当中。

inode 对象由 `inode` 结构体表示，操作函数则是由 `inode_operations` 结构体表示，都定义在文件 `include/linux/fs.h` 中，操作函数主要提供对 inode 成员变量的操作，同理，这些函数的具体实现由文件系统提供，VFS 只提供接口。

上述结构体都定义在文件 `include/linux/fs.h` 中。

#### dentry

VFS 也可以根据 inode 提供的信息来解析路径，但是由于路径解析是一个非常频繁的操作，且解析路径是一个耗时的操作，因此为了提高解析的性能，引入 dentry 对象。比如路径 /bin/pwd，/、bin、pwd 都是路径中的一个 dentry，各自也都有对应的 inode 对象。dentry 对象由 `dentry` 结构体表示，操作函数由 `dentry_operations` 结构体表示，都是定义在文件`include/linux/dache.h` 中。









