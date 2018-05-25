文件系统为内核和磁盘设备之间的数据交流提供了接口，Linux 作为一个开源的操作系统，本身是可以支持不同的文件系统，用户可以根据自身的需求选择不同特性的文件系统。
常见的文件系统有 ext2, ext3, ext4, proc, NFS, JFS, FAT 等。

### <font color=#00b0f0>虚拟文件系统</font>

虚拟文件系统是一个处于内核空间和文件系统之间的抽象层，虚拟文件系统对于需要访问的文件系统对象提供了通用的对象模型 (元数据, 文件数据)。同时还隐藏了不同文件系统之间的差异性，使得内核空间和用户空间不需要关心使用的到底是哪种文件系统，在切换文件系统后也无需修改内核空间和用户空间。下图显示了虚拟文件系统在操作系统中
的位置 (灵魂画手上线)：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/vfs.jpeg)

在用户眼里，文件系统就是一颗目录树。而实际上虚拟文件系统提供的对象模型并不是一颗树，而是下图的结构：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/fs-obj-model.jpeg)

比如执行 `cat /dir1/file1` 的查找过程如下：
1. 虚拟文件系统根据 dir1 这个文件名找到 inode 编号 10
2. 根据 inode 编号 10 找到对应的 data pooling
3. 根据 data pooling 中的 `file1 --> 12` 得到 file1 的 inode 编号 12
4. 根据 inode 编号 12 找到对应的 data pooling `a`
