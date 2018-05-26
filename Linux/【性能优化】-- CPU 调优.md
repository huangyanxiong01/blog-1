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

### <font color=#00b0f0>发现瓶颈</font>

想要快速确定一个问题是 CPU 造成的，其实不是一件很容易的事情，因为 CPU 需要跟不同的子系统互相通信，所以很多时候表现出来的只是表象，背后真相可能是其他子系统造成的问题。比如当 CPU 的利用率很高时，有可能是真的在高速地处理者任务，也有可能是因为某个系统事件阻塞在那里；或者在增加了 CPU 数量之后，发现进程服务的 CPU 占用还是非常高。

除了 [【性能优化】-- top](https://github.com/hsxhr-10/blog/blob/master/Linux/%E3%80%90%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%E3%80%91--%20top.md) 中提到的 `top`，下面介绍一些其他非常好用的 CPU 调优工具

#### vmstat

```
root@ubuntu:/proc/28941# vmstat 1 
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 0  0      0 270968 121320 443424    0    0     1    82   61   33  0  0 99  0  0
 0  0      0 270984 121320 443424    0    0     0     0   83  188  1  1 99  0  0
 0  0      0 270984 121320 443424    0    0     0     0   56  113  0  0 100  0  0
 
 ...
```

- r 代表正在运行的进程数。由此可以大概了解 繁忙程度
- b 代表阻塞的进程数。当这个值持续大于 0 时，可以推测
