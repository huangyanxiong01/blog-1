在[【故障排查】-- 高内存占用(1)](https://github.com/hsxhr-10/blog/blob/master/Linux/%E3%80%90%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5%E3%80%91--%20%E9%AB%98%E5%86%85%E5%AD%98%E5%8D%A0%E7%94%A8(1).md)
中讨论了 `gdb`, `pyrasite`, `guppy`, `objgraph` 等几个非常好用的故障排查工具，这里再了解一个同样好用的工具箱 --- gperftools。

gperftools 包含 4 个组件，TCMalloc, heap-checker, heap-profiler 和 cpu-profiler。其中第 1 个是优化过的内存管理器，后面 3 个是性能调优工具。gperftools 所提供的性能调优工具最大的特色是以函数调用关系为核心，通过生成一幅函数调用关系图快速且明确地告诉你，哪个函数占用的 CPU 时间最多，哪个函数占用的内存最多。

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

### <font color=#00b0f0>gperftools 安装</font>

```
sudo apt-get update -y
sudo apt-get install google-perftools -y
```

因为需要用到几个链接库，安装完成后，到 `/usr/lib` 下检查下 `libtcmalloc.so.4` 和 `libprofiler.so.0` 是否存在

---

### <font color=#00b0f0>TCMalloc</font>

TCMalloc 是 glibc 2.3 malloc 的一个优化替代方案。根据官方说法，TCMalloc 在 malloc/free 的操作上比 malloc 要快 6 倍左右，而且 TCMalloc 能产生更少的内存碎片，这对于高并发场景下的内存操作性能提升很大。关于 TCMalloc 和 malloc 的性能测试对比可以参考[这里](https://gperftools.github.io/gperftools/tcmalloc.html)

TCMalloc 的使用非常简单：

```
LD_PRELOAD=/usr/lib/libtcmalloc.so.4 python YOUR_SCRIPT.py
```

就这样，凡是 malloc 的地方都被 TCMalloc 替换掉了

---

### <font color=#00b0f0>heap-profiler</font>

heap-profiler 可以帮助我们排查内存泄漏问题，以[【故障排查】-- 高内存占用(1)](https://github.com/hsxhr-10/blog/blob/master/Linux/%E3%80%90%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5%E3%80%91--%20%E9%AB%98%E5%86%85%E5%AD%98%E5%8D%A0%E7%94%A8(1).md)
中的 `mock_high_memory_pure.py` 为例：

```
# 生成内存使用报告
root@ubuntu:/opt# LD_PRELOAD=/usr/lib/libtcmalloc.so.4 HEAPPROFILE=/tmp/profile python mock_high_memory_pure.py

# 在 /tmp 下可以看到非常多形如 profile.xxx.heap 的文件，我们挑最新的那个 (profile.3968.heap)

# 转换成图片格式
root@ubuntu:/tmp# google-pprof --gif `which python` /tmp/profile.3968.heap > 1.gif
```

打开 `1.gif`，看到一幅指定报告对应的函数调用关系图，如下：

![](https://raw.githubusercontent.com/oooooxooooo/picture/master/1.gif)

图片关键点解释：
- /usr/bin/python：执行该进程的命令
- Total MB：该报告所代表的时间点中，进程所占用的总内存
- 框：代表一个函数。以 `string_concatenate` 所在的框为例，`string_concatenate` 代表函数的名字；`0.0 (0.0%)` 代表 `string_concatenate` 本身占用的内存为 0.0，占 `Total MB` 的 0.0%；`of 63.7 (98.7%)` 代表 `string_concatenate` 的函数调用占用内存为 63.7 MB，
占 `Total MB` 的 98.7%
- 箭头：代表函数调用关系。以 `string_concatenate` 框所发出的箭头为例，指向了 `PyString_Resize` 框，也就是说在 `string_concatenate` 中调用了 `PyString_Resize`；箭头上的 `63.7` 代表了 `PyString_Resize` 这个函数调用占用了 63.7 MB 内存

通过 `1.gif` 可以很清楚地看到可能发生了内存问题的函数调用 (`PyString_Resize` 并不是我处理得这么大的，是这个工具特意将可能有问题的函数放大，方便查找)，也就是图中的 `PyString_Resize`。这是个 cpython 函数，对应到 python 就是像 `+=` 这样的字符串操作了，结合 `gdb` 这样的工具找到线程正在执行的代码的上下文，确实会发现有一个循环在不断执行该操作：

```
# mock_high_memory_pure.py

...

while 1:
    _pure_string += 'qwertyuioplkmsjafdkhjkhsdfajkjsalkdfjslkfjklsasl
    kajfklsjafkljslkfjskldfjlnmxcnvxznv,mnxzm,vnm,xuw
    ueiouriowerioqwurioweroiwq
    eushdjkfhskjadfhkjsadhbcxvnmbnmvbxnmvbnmxcbvmnxbvnmbxmn
    vbxcnmvbxcnmvbkdslkjsdflkjsdklfjsdlkfjklsjflks;fjlkasdjfklsjfl
    ksdjfklsdjfklsjfklsdjfklsdjkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
    kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
    kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
    kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
    kkkkkkkkkkkkkkkkkkkkkkkk'

...
```
---

### <font color=#00b0f0>cpu-profiler</font>

cpu-profiler 可以帮助我们排查高 CPU 占用问题，同样以 `mock_high_memory_pure.py` 为例：

```
# 生成 CPU 使用报告
root@ubuntu:/opt# LD_PRELOAD=/usr/lib/libprofiler.so.0  CPUPROFILE=/tmp/profile python mock_high_memory_pure.py

# 在 /tmp 下可以看到名为 profile 的文件

# 转换成图片格式
root@ubuntu:/tmp# google-pprof --gif `which python` /tmp/profile > 2.gif
```

打开 `2.gif`，看到一幅指定报告对应的函数调用关系图，如下：

![](https://raw.githubusercontent.com/oooooxooooo/picture/master/2.gif)


图片关键点解释：
- /usr/bin/python：执行该进程的命令
- Total samples：该报告所代表的时间点中，进程所占用的 CPU 时间
- 框：代表一个函数。以最大的 `PyString_Resize` 所在的框为例，`PyString_Resize` 代表函数的名字；`22 (46.8%)` 代表 `PyString_Resize` 本身占用的CPU 时间为 0.22 秒，占 `Total samples` 的 46.8%；`of 32 (68.1%)` 代表 `PyString_Resize` 的函数调用占用 CPU 时间为 0.32 秒，
占 `Total samples` 的 68.1%
- 箭头：代表函数调用关系。箭头旁边的数字代表了指向的函数调用所占用的 CPU 时间

通过 `2.gif` 可以推断这个进程的 CPU 占用比较正常，CPU 时间的使用集中在了 `PyString_Resize` 函数上

---

### <font color=#00b0f0>总结</font>

在[【故障排查】-- 高 CPU 占用](https://github.com/hsxhr-10/blog/blob/master/Linux/%E3%80%90%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5%E3%80%91--%20%E9%AB%98%20CPU%20%E5%8D%A0%E7%94%A8.md) 和[【故障排查】-- 高内存占用(1)](https://github.com/hsxhr-10/blog/blob/master/Linux/%E3%80%90%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5%E3%80%91--%20%E9%AB%98%E5%86%85%E5%AD%98%E5%8D%A0%E7%94%A8(1).md)中，都是先通过 gdb 来定位线程正在执行的代码上下文，但是这个上下文的范围往往不是很明确，如果不借助其他工具，多数只能带着猜测去验证，但是如果结合本文中的 gperftools，在定位到上下文范围的同时，进一步定位函数及函数调用关系，那么排查将会更加的稳。同时 gperftools 的各个工具还有很多参数可用，需要的可以参考下官方文档；在高并发场景下的内存优化不妨可以考虑下 TCMalloc，现在很多常用的服务组件在官方上已经支持 TCMalloc 了，比如 MySQL, Nginx, Redis
