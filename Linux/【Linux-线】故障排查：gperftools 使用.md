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

在[【Linux-线】故障排查：高内存占用(1).md](https://github.com/oooooxooooo/blog/blob/master/Linux/%E3%80%90Linux-%E7%BA%BF%E3%80%91%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5%EF%BC%9A%E9%AB%98%E5%86%85%E5%AD%98%E5%8D%A0%E7%94%A8(1).md)
中讨论了 `gdb`, `pyrasite`, `guppy`, `objgraph` 等非常好用的故障排查工具，这里再了解下一个非常好用的工具箱 --- gperftools。

gperftools 包含 4 个组件，TCMalloc, heap-checker, heap-profiler 和 cpu-profiler。其中第 1 个是优化过的内存管理器，后面 3 个是性能调优工具。gperftools 所提供的性能调优工具最大的特色是以函数调用关系为核心，通过生成一幅函数调用关系图快速且明确地告诉你，哪个函数占用的 CPU 时间最多，哪个函数占用的内存最多。

---

### <font color=#00b0f0>gperftools 安装</font>

```
sudo apt-get update -y
sudo apt-get install google-perftools -y
```

因为需要用到几个链接库，安装完成后，到 `/usr/lib` 下检查下 `libtcmalloc.so.4` 和 `libprofiler.so.0` 是否存在

---

### <font color=#00b0f0>TCMalloc</font>

TCMalloc 是 glibc 2.3 malloc 的一个优化替代方案。根据官方说法，TCMalloc 在 malloc/free 的操作上比 malloc 要快 6 倍左右，而且 TCMalloc 能产生更少的内存碎片，这对于高并发下的内存操作性能提升很大。关于 TCMalloc 和 malloc 的性能测试对比可以参考[这里](https://gperftools.github.io/gperftools/tcmalloc.html)

TCMalloc 的使用非常简单：

```
LD_PRELOAD=/usr/lib/libtcmalloc.so.4 python YOUR_SCRIPT.py
```

### <font color=#00b0f0>heap-profiler</font>

heap-profiler 可以帮助我们排查内存泄漏问题，以[【Linux-线】故障排查：高内存占用(1).md](https://github.com/oooooxooooo/blog/blob/master/Linux/%E3%80%90Linux-%E7%BA%BF%E3%80%91%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5%EF%BC%9A%E9%AB%98%E5%86%85%E5%AD%98%E5%8D%A0%E7%94%A8(1).md)
中的 `mock_high_memory_pure.py` 为例：

```
# 生成报告
root@ubuntu:/opt# LD_PRELOAD=/usr/lib/libtcmalloc.so.4 HEAPPROFILE=/tmp/profile python mock_high_memory_pure.py

# 在 /tmp 下可以看到非常多形如 profile.xxx.heap 的文件，我们挑最新的那个 (profile.3968.heap)

# 转换成图片格式
root@ubuntu:/tmp# google-pprof --gif `which python` /tmp/profile.3968.heap > 1.gif
```

打开 `1.gif`，如下：

![](https://raw.githubusercontent.com/oooooxooooo/picture/master/1.gif)














