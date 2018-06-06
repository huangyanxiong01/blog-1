### 概述

Linux 为了支持不同的文件系统，就需要一个抽象层将具体文件系统的细节屏蔽掉，只要文件系统的实现能遵循一定的规则，就能和这个抽象层顺利配合，并且抽象层对外提供统一的操作接口，让用户空间无论操作哪个文件系统都只需要作出一样的操作，这个抽象层就是虚拟文件系统 --- VFS。VFS 除了使 Linux 能够兼容不同的文件系统外，也使得跨文件系统操作和一切皆文件的哲学理念成为可能。

> 注意：以下没特殊说明的 superblock, inode, file 都是指 VFS 的

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

### 关于文件系统的三个概念

- 创建：格式化磁盘并创建文件系统，在创建文件系统的时候会在磁盘中写入该文件系统的 superblock (注意是文件系统的 superblock 而不是 VFS 的 superblock)
- 注册：向内核声明自己是能被支持的文件系统，注册过程就是对数据结构 `file_system_type` 的初始化
- 挂载：mount 操作

---

### VFS 数据结构

- superblock：超级块。表示某个加载的文件系统
- inode：索引节点。表示某个文件
- dentry：目录项。表示路径的一个组成部分
- file：文件对象。表示被某个进程打开的一个文件
- 文件系统相关
- 进程相关

> 这些对象都是存放于内存当中

#### superblock

superblock 存储着一个已挂载的文件系统的详细信息，代表一个已安装的文件系统。当有文件系统被挂载时，内核会从磁盘中读出该文件系统的 superblock 来填充 VFS 的 superblock。一个已挂载的文件系统和一个 superblock 一一对应。

superblock 的成员变量由结构 `struct super_block` 定义，常见的有：

- **s_type：文件系统类型**
- s_op：superblock 操作函数列表

superblock 的操作函数列表由 `super_operations` 结构体定义，常见的有：

- alloc_inode(sb)：初始化一个新的 inode
- destroy_inode(inode)：释放 inode
- read_inode(inode)：磁盘中的文件系统 inode 并填充到内存中 VFS 的 inode
- write_inode(inode, wait)：将内存中 VFS 的 inode 写入磁盘中文件系统的 inode

这些函数都由具体的文件系统实现，VFS 只提供接口名。上述结构体都定义在文件 `include/linux/fs.h` 中。

#### inode

inode 存储了一个文件的详细信息，代表了一个真实的物理文件。当一个文件被首次访问时，内核会利用 superblock 提供的操作函数将磁盘中的文件系统的 inode 读出来，并填充到内存中 VFS 的 inode。形象点来说，执行 `ls -l` 时的信息都是 inode 提供的。

inode 的成员变量由 `inode` 结构体表示，常见的有：

- **i_sb：与之对应的 superblock**
- **i_fop：该 inode 对应的 file 的操作函数列表 (很重要！用户空间的 I/O 操作都会被转到这里)**
- i_op：inode 操作函数列表

inode 的操作函数列表由 `inode_operations` 结构体表示，常见的有：

- create(dir, dentry, mode, nameidata)：为 dentry 创建一个新的 inode

这些函数的具体实现由文件系统提供，VFS 只提供接口。上述结构体都定义在文件 `include/linux/fs.h` 中。

#### dentry

dentry 概念的引入主要是为了更快速地解析路径、查找文件。由于路径解析是一个非常频繁的操作，且解析路径是一个耗时的操作，因此为了提高解析的性能，引入 dentry 对象，并将 dentry 对象缓存起来，这样在每次需要解析路径时，就快很多了。比如路径 /bin/pwd，/、bin、pwd 都是路径中的一个 dentry。不同于前面的两个对象，dentry 没有对应的磁盘数据结构，VFS 在解析路径名的过程中现场将它们逐个地解析成 dentry，并缓存起来。

dentry 的成员变量由 `dentry` 结构体表示，常见的有：

- **d_inode：与之对应的 inode 对象**
- d_op：dentry 操作函数列表

dentry 对象的操作函数列表由 `dentry_operations` 结构体表示，常见的有：

- d_revalidate(dentry)：判断 dentry 是否有效
- d_hash(dentry, qstr)：为 dentry 生成缓存用的散列值

这些函数的具体实现由文件系统提供，VFS 只提供接口。上述结构体都定义在文件 `include/linux/fs.h` 中。

#### file

file 是已打开的文件在内存中的表示，主要用于建立进程、VFS、文件系统、磁盘文件几者的联系。用户空间的进程看到的只是 file，而不用关心 superblock, inode, dentry 等对象。file 对应的就是磁盘中的文件，他们之间的关系就像是进程和程序文件的关系。一个文件可以被多个进程同时打开，所以文件的 file 可以不唯一，但是文件的 inode 和 dentry 肯定是唯一的。

file 的成员变量由 `file` 结构体表示，常见的有：

- **f_dentry：与之对应的 dentry 对象**
- f_op：file 操作函数列表

file 的操作函数列表由 `file_operations` 结构体表示，常见的有：

- open(inode, file)：文件打开操作
- read(file, __user, size_t， loff_t)：文件读操作
- write(file, __user, size_t， loff_t)：文件写操作

这些函数的具体实现由文件系统提供，VFS 只提供接口。上述结构体都定义在文件 `include/linux/fs.h` 中。

#### 文件系统相关

和文件系统相关的数据结构有两个，`file_system_type` 和 `vfsmount`。只要发生文件系统创建，就会有且只有一个 `file_system_type` 被初始化，`file_system_type` 代表文件系统类型。而每当有文件系统挂载时，就会有一个 `vfsmount` 被初始化，`vfsmount` 代表挂载点。

#### 进程相关

和进程相关的数据结构主要是 `files_struct`，代表进程打开的文件信息，关键的成员变量如下：

- **fd：进程的 file 数组 (很重要！文件 A  的文件描述符就是文件 A 对应的 file 在该数组中的索引)**
- max_fds：file 数的上限
- max_fdset：文件描述符的上限
- open_fds：打开的文件描述符数组
- close_on_exec：关闭的文件描述符数组

---

### 数据结构之间的联系

上述的各个数据结构当然不是孤立存在的，正是由于它们的相互合作，才能让 VFS 很好滴工作。下图是描述它们之间的联系。

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/VFS%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E4%B9%8B%E9%97%B4%E7%9A%84%E8%81%94%E7%B3%BB.jpg)

当有文件系统创建时 (被 Linux 支持的文件系统)，内核初始化唯一一个与该文件系统对应的 `file_system_type`；当有文件系统挂载时，内核就会初始化一个 `vfsmount` 和一个 superblock；通过 `file_system_type` 可以找到对应的 superblock，通过 superblock 也可以找到对应的 `file_system_type`。

用户进程 --> syscall --> VFS --> FS 的过程 (先不考虑 Page Cache Layer)：

1. 无论是 sys_read 还是 sys_write，都需要先调用 sys_open 打开文件，打开文件时会初始化 `files_struct`
2. 根据 `files_struct` 的 `fd` 找到对应的 file
3. 根据 file 的 `f_dentry` 找到对应的 dentry
4. 根据 dentry 的 `d_inode` 找到对应的 inode
5. 根据 inode 的 `i_fop` 和 syscall 的类型，找到对应的操作函数接口
6. 根据 inode 的 `i_sb` 找到对应的 superblock
7. 根据 superblock 找到对应的文件系统
8. VFS 将控制权交给该文件系统，并传递要执行的函数接口
9. 文件系统判断要操作的文件类型 (f/c/b/s)，并调用自身实现的函数接口向下层继续发出 I/O 请求 (下层结构请参考[分层模型](https://raw.githubusercontent.com/hsxhr-10/picture/master/%E5%9D%97%E8%AE%BE%E5%A4%87%E5%88%86%E5%B1%82%E5%9B%BE2.jpg))。

