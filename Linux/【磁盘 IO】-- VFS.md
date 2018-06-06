### 概述

Linux 为了支持不同的文件系统，就需要一个抽象层将具体文件系统的细节屏蔽掉，只要文件系统的实现能遵循一定的规则，就能和这个抽象层顺利配合，并且抽象层对外提供统一的操作接口，让用户空间无论操作哪个文件系统都只需要作出一样的操作，这个抽象层就是虚拟文件系统 --- VFS。VFS 除了使 Linux 能够兼容不同的文件系统外，也使得跨文件系统操作和一切皆文件的哲学理念成为可能。

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

- **superblock**：超级块。表示某个加载的文件系统
- **inode**：索引节点。表示某个文件
- **dentry**：目录项。表示路径的一个组成部分
- **file**：文件对象。表示被某个进程打开的一个文件

> 这些对象都是存放于内存当中

#### superblock

superblock 存储着一个已挂载的文件系统的详细信息，代表一个已安装的文件系统。当有文件系统被挂载时，内核会从磁盘中读出该文件系统的 superblock 来填充 VFS 的 superblock。一个已挂载的文件系统和一个 superblock 一一对应。

superblock 的成员变量由结构 `struct super_block` 定义，常见的有：

- **s_type：文件系统类型**
- **s_op：superblock 操作函数列表**

superblock 的操作函数由 `super_operations` 结构体定义，常见的有：

- **alloc_inode(sb)：初始化一个新的 inode**
- **destroy_inode(inode)：释放 inode**
- **read_inode(inode)：磁盘中的文件系统 inode 并填充到内存中 VFS 的 inode**
- **write_inode(inode, wait)：将内存中 VFS 的 inode 写入磁盘中文件系统的 inode**

这些函数都由具体的文件系统实现，VFS 只提供接口名。上述结构体都定义在文件 `include/linux/fs.h` 中。

#### inode

inode 存储了一个文件的详细信息，代表了一个真实的物理文件；当一个文件被首次访问时，内核会利用 superblock 提供的操作函数将磁盘中文件系统的 inode 读出来，并填充到内存中 VFS 的 inode。形象点来说，执行 `ls -l` 时的信息都是 inode 提供的。

inode 的成员变量由 `inode` 结构体表示，常见的有：

- **i_dentry：与之对应的 dentry 链表**
- **i_sb：与之对应的 superblock**
- **i_op：inode 操作函数列表**
- **i_fop：该 inode 对应的 file 的操作函数列表 (很重要！用户空间的 I/O 操作都会被转到这里)**

inode 的操作函数由 `inode_operations` 结构体表示，常见的有：

- **create(dir, dentry, mode, nameidata)：为 dentry 创建一个新的 inode**

这些函数的具体实现由文件系统提供，VFS 只提供接口。上述结构体都定义在文件 `include/linux/fs.h` 中。

#### dentry

VFS 也可以根据 inode 提供的信息来解析路径，但是由于路径解析是一个非常频繁的操作，且解析路径是一个耗时的操作，因此为了提高解析的性能，引入 dentry 对象，并将 dentry 对象缓存起来，这样在每次需要解析路径时，就快很多了。比如路径 /bin/pwd，/、bin、pwd 都是路径中的一个 dentry，各自也都有对应的 inode 对象。不同于前面两个对象，这个对象在文件系统中并没有对应的磁盘数据。

dentry 对象的成员变量由 `dentry` 结构体表示，常见的有：

- **d_inode：与之对应的 inode 对象**
- **d_sb：与之对应的 superblock 对象**
- d_parent：：父目录组成的 dentry 对象链表
- d_subdirs：子目录的 dentry 对象
- d_vfs_flags：dentry 对象缓存标志
- d_op：操作函数

dentry 对象的操作函数由 `dentry_operations` 结构体表示，常见的有：

- d_delete(dentry)：删除 dentry 对象

这些函数的具体实现由文件系统提供，VFS 只提供接口。上述结构体都定义在文件 `include/linux/fs.h` 中。

#### file

file 对象和文件的关系就像是进程和程序的关系。file 对象表示被进程打开的文件 (在内存而非磁盘中的文件)。当进程 A 打开了文件 x 时，就会产生一个 file 对象，假设进程 A 和 B 同时打开了文件 x，那么就会产生两个 file 对象。开发可能对于这个对象相比前三个对象更熟悉，因为 VFS 对用户可见的一般来说就是文件，用户进程操作得最多的也是文件，而不是 superblock, inode 或者 dentry。一个文件的 file 对象可能不是唯一的，但是 inode 对象和 dentry 对象肯定是唯一的。跟 dentry 对象类似，file 对象在文件系统上也没有对应的磁盘数据。

file 对象的成员变量由 `file` 结构体表示，常见的有：

- **f_dentry：与之对应的 dentry 对象**
- f_mode：文件的访问模式
- f_pos：文件当前的位移量
- f_op：操作函数

file 对象的操作函数由 `file_operations` 结构体表示，常见的有：

- open
- read
- write
- mmap
- flush

---

### 进程, superblock, inode, dentry, file, 文件系统, 之间的关系

当一个进程向一个文件发出 I/O 操作时，进程、VFS、文件系统之间发生了什么？想要弄清楚这个问题还需要了解一下进程与文件相关的数据结构 `files_struct`。

`files_struct` 重要的成员变量有：

- fd：进程相关的 file 对象数组
- max_fds：文件对象数的上限
- max_fdset：文件描述符的上限
- open_fds：打开的文件描述符数组
- close_on_exec：关闭的文件描述符数组

**文件描述符就是 `fd` 变量中某个 file 对象的数组索引**。当一个进程打开某个文件时，进程的 `files_struct` 就会得到进行初始化，对于开发人员来说，操作文件就是操作对应的文件描述符，对于进程来说，操作文件就是操作 file 对象。

拿写操作举例来说，进程不断向 file 对象发出写 I/O 操作，file 对象本身并不知道自己是否应该回写磁盘，主要是通过自身的`f_dentry` 变量找到对应的 `dentry` 对象 => 根据 dentry 对象中的 `d_inode` 变量找到 inode 对象 => 根据 inode 对象中的 `i_sb` 变量找到 superblock 对象 => superblock 对象根据 `s_dirty` 和 `s_io` 等信息决定是否需要回写 file 对象，如果有需要那就调用 superblock 对象的回写函数，将数据回写到下层 FS Layer => Generic Block Layer => ... => Block Device Layer (参考[分层模型](https://raw.githubusercontent.com/hsxhr-10/picture/master/%E5%9D%97%E8%AE%BE%E5%A4%87%E5%88%86%E5%B1%82%E5%9B%BE2.jpg))。

---

本文较为详细地介绍了 VFS 的 4 大对象，并且分析了 “进程 <--> VFS <--> 文件系统” 三者之间如何工作的。
