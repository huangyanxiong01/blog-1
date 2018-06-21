### <font color=#00b0f0>运行环境</font>

```
# uname -a
Linux ubuntu 3.16.0-30-generic #40~14.04.1-Ubuntu SMP Thu Jan 15 17:43:14 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux

# cat /etc/*-release
DISTRIB_DESCRIPTION="Ubuntu 14.04.2 LTS"

# 内存：2G
# CPU：2核
```

---

### 概述

对于一般的高 iowait 问题的解决思路如下：`iostat` 了解 I/O 环境 --> `iotop` 定位问题进程 --> `lsof` 定位问题文件 --> 由文件定位源码位置。

#### 1. iostat

通过 `iostat` 命令查看 I/O 的合并情况、读频繁还是写频繁、读写的数据量、I/O 队列长度、iowait 等信息，对 I/O 有个总体的把握，关于 `iostat` 可以参考 [这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【内置工具】--%20iostat.md)。演示如下：

```
shell> iostat -xmtp

06/19/2018 07:24:42 AM
avg-cpu:  %user   %nice %system %iowait  %steal   %idle
          43.15    0.00   10.66    0.00    0.00   46.19

Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
sda               0.00    13.00    0.00  298.00     0.00   144.06   990.07     9.52   31.97    0.00   31.97   1.14  34.00
sda1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sda2              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sda5              0.00    13.00    0.00  297.00     0.00   144.06   993.40     9.52   32.08    0.00   32.08   1.14  34.00
dm-0              0.00     0.00    0.00  310.00     0.00   144.06   951.74     9.70   31.29    0.00   31.29   1.10  34.00
dm-1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
...
```

#### 2. iotop

通过 `iotop` 命令查看高 I/O 负载的进程，得到 PID。演示如下：

```
shell> iotop

Total DISK READ :       0.00 B/s | Total DISK WRITE :      86.46 M/s
Actual DISK READ:       0.00 B/s | Actual DISK WRITE:      77.70 M/s
  TID  PRIO  USER     DISK READ  DISK WRITE  SWAPIN     IO>    COMMAND                                                                                      
 3697 be/4 root        0.00 B/s   86.46 M/s  0.00 %  0.00 % python high_iowait.py
```

#### 3. lsof

根据得到的 PID，通过 `lsof` 命令配合 `watch` 命令观察高负载进程对应的高负载文件。演示如下：

```
shell> watch lsof -p 3697

Every 2.0s: lsof -p 3697                                                                                                            Tue Jun 19 07:43:12 2018

COMMAND  PID USER   FD   TYPE DEVICE    SIZE/OFF    NODE NAME
python  3697 root  cwd    DIR  252,0        4096 1179649 /opt
python  3697 root  rtd    DIR  252,0        4096       2 /
python  3697 root  txt    REG  252,0     3341288 3282536 /usr/bin/python2.7
python  3697 root  mem    REG  252,0     2919792 3281469 /usr/lib/locale/locale-archive
python  3697 root  mem    REG  252,0     1071552 1577260 /lib/x86_64-linux-gnu/libm-2.19.so
python  3697 root  mem    REG  252,0      100728 1573150 /lib/x86_64-linux-gnu/libz.so.1.2.8
python  3697 root  mem    REG  252,0       10680 1577251 /lib/x86_64-linux-gnu/libutil-2.19.so
python  3697 root  mem    REG  252,0       14664 1577265 /lib/x86_64-linux-gnu/libdl-2.19.so
python  3697 root  mem    REG  252,0     1857312 1577261 /lib/x86_64-linux-gnu/libc-2.19.so
python  3697 root  mem    REG  252,0      141574 1577262 /lib/x86_64-linux-gnu/libpthread-2.19.so
python  3697 root  mem    REG  252,0      149120 1577269 /lib/x86_64-linux-gnu/ld-2.19.so
python  3697 root    0u   CHR  136,3         0t0       6 /dev/pts/3
python  3697 root    1u   CHR  136,3         0t0       6 /dev/pts/3
python  3697 root    2u   CHR  136,3         0t0       6 /dev/pts/3
python  3697 root    3u   REG  252,0 16149295104 3686436 /opt/build_img.sh

# 几秒后
Every 2.0s: lsof -p 3697                                                                                                            Tue Jun 19 07:44:13 2018

COMMAND  PID USER   FD   TYPE DEVICE    SIZE/OFF    NODE NAME
python  3697 root  cwd    DIR  252,0        4096 1179649 /opt
python  3697 root  rtd    DIR  252,0        4096       2 /
python  3697 root  txt    REG  252,0     3341288 3282536 /usr/bin/python2.7
python  3697 root  mem    REG  252,0     2919792 3281469 /usr/lib/locale/locale-archive
python  3697 root  mem    REG  252,0     1071552 1577260 /lib/x86_64-linux-gnu/libm-2.19.so
python  3697 root  mem    REG  252,0      100728 1573150 /lib/x86_64-linux-gnu/libz.so.1.2.8
python  3697 root  mem    REG  252,0       10680 1577251 /lib/x86_64-linux-gnu/libutil-2.19.so
python  3697 root  mem    REG  252,0       14664 1577265 /lib/x86_64-linux-gnu/libdl-2.19.so
python  3697 root  mem    REG  252,0     1857312 1577261 /lib/x86_64-linux-gnu/libc-2.19.so
python  3697 root  mem    REG  252,0      141574 1577262 /lib/x86_64-linux-gnu/libpthread-2.19.so
python  3697 root  mem    REG  252,0      149120 1577269 /lib/x86_64-linux-gnu/ld-2.19.so
python  3697 root    0u   CHR  136,3         0t0       6 /dev/pts/3
python  3697 root    1u   CHR  136,3         0t0       6 /dev/pts/3
python  3697 root    2u   CHR  136,3         0t0       6 /dev/pts/3
python  3697 root    3u   REG  252,0 21389893632 3686436 /opt/build_img.sh
```

观察 `SIZE/OFF` 字段，发现文件 `/opt/build_img.sh` 的变化非常快，且很大，说明这个文件正在进行频繁的 I/O 操作。定位到问题文件了！

#### 4. 源码

如果这个进程是自己写的代码，则根据高负载文件定位到源码位置，从而结合源码进一步分析问题原因。如果进程是一些开源软件，那就搞清楚这个高负载文件对于进程的意义，看是否存在什么配置错误，如果还不能找到原因就根据文件定位到源码进一步分析。




















