### <font color=#00b0f0>了解虚拟文件系统</font>

在 Linux 下所有的数据都是通过文件的形式存储的。文件的常见类型有文本和二进制两种，但是虚拟文件系统却含有其他类型的文件，最常见的虚拟文件系统就是 /proc 了。

虚拟文件系统下的虚拟文件相比普通的文件是特别的，它们的大小通常是 0 byte，但是却并非是真的空文件。并且它们的时间属性通常是系统的当前时间，因为这些文件经常会被实时更新。

除了系统调用，虚拟文件系统是另外一个用户空间和内核空间的交互接口，用户空间通过虚拟文件系统可以查看内核空间发生的事情，甚至修改相关虚拟文件，从未达到影响内核空间。像 `/proc/interrupts`, `/proc/meminfo`, `/proc/mounts` 和 `/proc/partitions` 这样的虚拟文件提供了系统硬件的实时信息，而其他一些像 `/proc/filesystems` 和 `/proc/sys/` 就提供系统的配置信息和配置接口。

虚拟文件系统的目录组织是很清晰的，不通的信息都被分门别类到了不通的目录下，像 `/proc/ide/` 目录就包含了物理 IDE 设备的信息，进程目录就包含了系统中所有有效进程的运行时信息。

---

### <font color=#00b0f0>虚拟文件系统的用途</font>

虚拟文件系统有两种用途，一是通过查看虚拟文件了解系统信息，二是通过修改虚拟文件改变系统配置。

绝大部分的虚拟文件都是可以通过 `less`, `cat`, `more` 等文件查看命令进行查看，但是也有一些是只能通过像 `open`, `read`, `write` 等系统调用进行查看或修改。而且在修改虚拟文件时，一般是不实用编辑器的，而是通过像 `echo www.example.com > /proc/sys/kernel/hostname ` 这样的 `echo` 命令去修改。

---

### <font color=#00b0f0>运行环境</font>

```
# uname -a
Linux ubuntu 3.16.0-30-generic #40~14.04.1-Ubuntu SMP Thu Jan 15 17:43:14 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux

# python2 --version
Python 2.7.9

# cat /etc/*-release
DISTRIB_DESCRIPTION="Ubuntu 14.04.2 LTS"

# 2G 内存
# CPU：2核
```

---

### <font color=#00b0f0>与 proc 同一层的文件</font>

**进程目录**

/proc 下面有很多以数字命名的目录，这些数字代表的就是进程的 PID，每个目录下面包含很多跟这个进程相关的详细信息：

```
root@ubuntu:/proc# ls | grep -E "[0-9]*"
1
10
100
1078
11
1112
1116
112
1121

...
```





---

### <font color=#00b0f0>proc 中的文件</font>
