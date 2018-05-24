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

**1、进程目录**

/proc 下面有很多以数字命名的目录，如下：

```
root@ubuntu:/proc# ll -h | grep -E "[0-9]*"
total 4.0K
dr-xr-xr-x 187 root       root          0 May 22 23:02 ./
drwxr-xr-x  22 root       root       4.0K Feb 25 03:19 ../
dr-xr-xr-x   9 root       root          0 May 22 23:03 1/
dr-xr-xr-x   9 root       root          0 May 22 23:03 10/
dr-xr-xr-x   9 root       root          0 May 22 23:03 100/
dr-xr-xr-x   9 root       root          0 May 22 23:03 1078/
dr-xr-xr-x   9 root       root          0 May 22 23:03 11/
dr-xr-xr-x   9 root       root          0 May 22 23:03 1112/
dr-xr-xr-x   9 root       root          0 May 22 23:03 1116/
dr-xr-xr-x   9 root       root          0 May 22 23:03 112/
dr-xr-xr-x   9 root       root          0 May 22 23:03 1121/

...
```

这些以数字命名的目录都叫做进程目录，数字代表的是进程的 PID，同时，这些目录里面也包含该进程相关的详细信息。每个进程目录的 owner 和 group 都和运行该进程的用户对应。当进程运行结束时，对应的进程目录也会消失，比如 `1121` 进程退出了，`/proc/1121` 目录也会消失。

每一个进程目录都会包含下面的文件 (以 11739 进程目录为例)：

- **cmdline** -- 启动进程的命令
```
root@ubuntu:/proc/11739# more cmdline 
sshd: root@pts/0
```

- **cwd** -- 符号链接，进程当前运行目录
```
root@ubuntu:/proc/11739# ll cwd
lrwxrwxrwx 1 root root 0 May 24 01:45 cwd -> //
```

- **environ** -- 进程的环境变量列表
```
root@ubuntu:/proc/11739# more environ 
# 空的
```

- **exe** -- 符号链接，执行进程的命令
```
root@ubuntu:/proc/11739# ll exe 
lrwxrwxrwx 1 root root 0 May 24 01:45 exe -> /usr/sbin/sshd*
```

- **fd** -- 进程使用到的文件描述符
```
root@ubuntu:/proc/11739# ll fd
total 0
dr-x------ 2 root root  0 May 24 01:45 ./
dr-xr-xr-x 9 root root  0 May 24 01:45 ../
lrwx------ 1 root root 64 May 24 01:45 0 -> /dev/null
lrwx------ 1 root root 64 May 24 01:45 1 -> /dev/null
lrwx------ 1 root root 64 May 24 01:48 10 -> /dev/ptmx
lrwx------ 1 root root 64 May 24 01:48 11 -> /dev/ptmx
lrwx------ 1 root root 64 May 24 01:45 2 -> /dev/null
lrwx------ 1 root root 64 May 24 01:45 3 -> socket:[57097]
lrwx------ 1 root root 64 May 24 01:45 4 -> socket:[58153]
lr-x------ 1 root root 64 May 24 01:45 5 -> pipe:[57226]
l-wx------ 1 root root 64 May 24 01:48 6 -> pipe:[57226]
l-wx------ 1 root root 64 May 24 01:48 7 -> /run/systemd/sessions/5.ref|
lrwx------ 1 root root 64 May 24 01:48 8 -> /dev/ptmx
```

- **maps** -- 进程 (线程) 中相邻虚拟内存信息
```
# ddress            # perms   # offset    # dev    # inode    # pathname
08048000-08056000   r-xp      00000000    03:0c    64593      /usr/sbin/gpm`
...

# 字段解析
# ddress：进程虚拟内存空间的开始地址-结束地址
# perms：permissions 的缩写，进程对该虚拟内存的权限。完整的权限是 `r/w/x/p`， 分别代表读/写/执行/共享，`-` 代表没有这个权限。如果进程在做了越权的操作会产生分段错误，可以通过系统调用 `mprotect` 去修改权限
# offset：如果该段虚拟内存区域是通过 `mmap` 映射文件而来的，那么 offset 的值代表从文件的哪里开始映射，如果不是从文件映射而来的，这个值只能是 0
# dev：device 的缩写，如果该段虚拟内存区域是通过 `mmap` 映射文件而来的，那么 dev 就代表该文件所在的主要设备和次要设备的编号，以 `:` 分割
# inode：如果该段虚拟内存区域是通过 `mmap` 映射文件而来的，那么 inode 就代表文件的 inode
# pathname：如果该段虚拟内存区域是通过 `mmap` 映射文件而来的，那么 pathname 就代表文件的绝对路径
```

- **mem**：只能通过 `open`, `read`, `write` 等系统调用使用

- **root**：符号链接，进程对应的 root 目录
```
root@ubuntu:/proc/11739# ll root
lrwxrwxrwx 1 root root 0 May 24 01:45 root -> //
```

- **stat**：进程状态信息，可读性差，一般给 `ps` 这样的系统命令使用
```
root@ubuntu:/proc/11739# cat stat
11739 (sshd) S 1158 11739 11739 0 -1 4219136 711 43352 0 0 33 119 167 23 20 0 1 0 9616123 122183680 1769 18446744073709551615 139907021352960 139907022099308 140735977982752 140735977979720 139906984753331 0 0 4096 81926 18446744071580841145 0 0 17 0 0 0 0 0 0 139907024196480 139907024210800 139907033661440 140735977987894 140735977987915 140735977987915 140735977988073 0
```

- **status**：进程状态信息，相比 `stat` 可读性更好
```
root@ubuntu:/proc/11739# more status 
Name:	sshd
State:	S (sleeping)
Tgid:	11739
Ngid:	0
Pid:	11739
PPid:	1158
TracerPid:	0
Uid:	0	0	0	0
Gid:	0	0	0	0
FDSize:	64
Groups:	
VmPeak:	  119328 kB
VmSize:	  119320 kB
VmLck:	       0 kB
VmPin:	       0 kB
VmHWM:	    7076 kB
VmRSS:	    7076 kB
VmData:	     752 kB
VmStk:	     136 kB
VmExe:	     732 kB
VmLib:	    8556 kB
VmPTE:	     252 kB
VmSwap:	       0 kB
Threads:	1
SigQ:	0/3855
SigPnd:	0000000000000000
ShdPnd:	0000000000000000
SigBlk:	0000000000000000
SigIgn:	0000000000001000
SigCgt:	0000000180014006
CapInh:	0000000000000000
CapPrm:	0000003fffffffff
CapEff:	0000003fffffffff
CapBnd:	0000003fffffffff
Seccomp:	0
Cpus_allowed:	ffffffff
Cpus_allowed_list:	0-31
Mems_allowed:	00000000,00000001
Mems_allowed_list:	0
voluntary_ctxt_switches:	9976
nonvoluntary_ctxt_switches:	5025
```

- Name：运行该进程的命令
- Tgid：线程组 id
- VmPeak：进程占用的虚拟内存的峰值大小
- VmSize：进程占用的虚拟内存大小
- VmRSS：虚拟内存对应的物理内存大小
- VmHWM：虚拟内存对应的物理内存的峰值大小
- VmLib：虚拟内存中共享内存的大小
- VmPTE：page table 的大小
- Threads：进程包含的线程数
- VmData, VmStk, VmExe：进程的数据、调用栈、文本段的虚拟内存大小
- Cpus_allowed：进程是否可以使用 cpu，如果改值符合 `Cpus_allowed_list` 范围则代表 ok
- Cpus_allowed_list：获取了 cpu 时间的 `Cpus_allowed` 标记范围
- Mems_allowed：进程是否可以使用内存，如果改值包含了 `Cpus_allowed_list` 则代表 ok
- Mems_allowed_list：可以使用内存的标记
- voluntary_ctxt_switches, nonvoluntary_ctxt_switches：进程主动、被动的上下文切换次数

---

### <font color=#00b0f0>proc 中的文件</font>
