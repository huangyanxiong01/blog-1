### <font color=#00b0f0>运行环境</font>

```
# uname -a
Linux ubuntu 3.16.0-30-generic #40~14.04.1-Ubuntu SMP Thu Jan 15 17:43:14 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux

# python2 --version
Python 2.7.9

# cat /etc/*-release
DISTRIB_DESCRIPTION="Ubuntu 14.04.2 LTS"
```

---

### <font color=#00b0f0>造成高内存占用的重要原因</font>

- **一般存在于一个类似死循环的结构，出问题的点就在这个结构中。因为如果进程不是持续运行，那么在运行结束后会释放占用资源**
- **在类死循环结构中，可能存在因违反了该门编程语言垃圾回收机制，而导致的大内存占用对象**
- **在类死循环结构中，可能存在单纯的大内存占用对象**

---

### <font color=#00b0f0>排查工具</font>

**ps**：定位进程中的高内存占用线程

**gdb**：定位进程/线程正在执行哪行代码

**pyrasite**：提供一个类似 ipython 的交互式环境去调试正在运行的进程

**guppy**：获取进程中各种对象的内存占用情况，用于判断是否存在大内存占用对象

**objgraph**：生成一副对象引用图，用于判断是否存在违反垃圾回收机制的对象

**dot**：将 dot 格式转换成 png 格式

安装方法：

```
apt-get install gdb
apt-get install python-dbg
apt-get install xdot
pip install pyrasite
pip install guppy
pip install objgraph
```

*注意，下面的案例以 python 语言为例，对于其他编程语言也会存在相似的排查工具，比如 java 的 jmap 等*

---

### <font color=#00b0f0>排查步骤</font>

根据 “**造成高内存占用的重要原因** ” 可知，常见的情况分别是**存在因违反垃圾回收机制导致的大内存占用对象**和**存在单纯的大内存占用对象**，下面用两个案例模拟这两种情况的排查步骤

**案例一：存在因违反垃圾回收机制导致的大内存占用对象**

对于 Python 语言来说，想要违反垃圾回收机制需要满足以下两点：

- 存在循环引用
- 循环引用链上的若干对象自定义了 `__del__` 方法

一个用于模拟循环引的脚本 `mock_high_memory_cycle.py`，内容如下：

```
# -*- coding=utf-8 -*-

import time


class ObjectA(object):

    def __del__(self):
        # 自定义的 __del__ 方法
        print 'ObjectA __del__'


class ObjectB(object):

    def __del__(self):
        # 自定义的 __del__ 方法
        print 'ObjectB __del__'


def main():
    obj_a = ObjectA()
    obj_b = ObjectB()
    # 发生循环引用
    obj_a.__attr = obj_b
    obj_b.__attr = obj_a


if __name__ == '__main__':
    # 持续执行
    while 1:
        main()
        # 控制内存泄漏的速度，避免太快被 OOM 机制制裁，而无法观察
        time.sleep(0.0001)

```

运行 `mock_high_memory_cycle.py` 等待 3 分钟，通过 `top` 已经可以看到进程的内存占用从一开始的 2.5% 飙升到 50.1%，可以开始排查

```
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
19460 root      20   0   42880  25476   4388 S  11.0  2.5   0:00.66 python mock_high_memory_cycle.py
```

```
PID USER      PR  NI    VIRT    RES     SHR S  %CPU %MEM     TIME+ COMMAND
19460 root      20   0   42880  25476   4388 S  11.0  50.1   0:00.66 python mock_high_memory_cycle.py
```

1、ps 定位进程中的高内存占用线程

```
root@ubuntu:~# ps H -eo user,pid,ppid,tid,time,%cpu,%mem,cmd --sort=-%mem | head -9

USER       PID  PPID   TID     TIME %CPU %MEM CMD
root     19460  5656 19460 00:00:20  3.6 57.3 python mock_high_memory_cycle.py
root       956     1   956 00:00:37  0.0  2.0 /usr/bin/dockerd --raw-logs
root       956     1  1040 00:00:52  0.0  2.0 /usr/bin/dockerd --raw-logs
root       956     1  1042 00:00:00  0.0  2.0 /usr/bin/dockerd --raw-logs
root       956     1  1043 00:00:00  0.0  2.0 /usr/bin/dockerd --raw-logs
root       956     1  1044 00:00:37  0.0  2.0 /usr/bin/dockerd --raw-logs
root       956     1  1123 00:00:34  0.0  2.0 /usr/bin/dockerd --raw-logs
root       956     1  1164 00:00:36  0.0  2.0 /usr/bin/dockerd --raw-logs
root       956     1  1566 00:00:07  0.0  2.0 /usr/bin/dockerd --raw-logs
```

可以看到进程 19460 只含有一个线程，即 TID 19460 就是高内存占用线程

2、gdb 定位线程调用栈

```
# 敲入 gdb，进入交互界面

# 连接上要调试的进程
(gdb) attach 19460
Attaching to process 19460
...

# 查看基本线程信息
(gdb) info threads
  Id   Target Id         Frame 
* 1    Thread 0x7f7f3d953740 (LWP 19460) "python" 0x00007f7f3d2518b3 in __select_nocancel () at ../sysdeps/unix/syscall-template.S:81

# 切换线程
(gdb) thread 1
[Switching to thread 1 (Thread 0x7f7f3d953740 (LWP 19460))]
#0  0x00007f7f3d2518b3 in __select_nocancel () at ../sysdeps/unix/syscall-template.S:81
81  in ../sysdeps/unix/syscall-template.S

# 查看线程调用栈
(gdb) bt
#0  0x00007f7f3d2518b3 in __select_nocancel () at ../sysdeps/unix/syscall-template.S:81
#1  0x000000000048052a in floatsleep (secs=<optimized out>) at ../Modules/timemodule.c:948
#2  time_sleep.72194 (self=<optimized out>, args=<optimized out>) at ../Modules/timemodule.c:206
#3  0x00000000004c7f54 in call_function (oparg=<optimized out>, pp_stack=0x7fff16beb7a0) at ../Python/ceval.c:4020
#4  PyEval_EvalFrameEx (f=f@entry=Frame 0x7f7f3d8f9050, for file mock_high_memory_cycle.py, line 34, in <module> (), throwflag=throwflag@entry=0) at ../Python/ceval.c:2666
...
```

从 `bt` 的 `#4` 可以看出线程 19460 正在执行的代码上下文是 `mock_high_memory_cycle.py` 34 行附近，对应源码找到这个上下文：

```
if __name__ == '__main__':
    while 1:
        main()
        time.sleep(0.0001)
```

找到了一个持续执行的死循环，并且确定了问题发生在 `main()` 中。至此，问题范围被大大缩小了，我们可以将注意力摆到 `main()` 函数上了

3、pyrasite 交互式调试

guppy 和 objgraph 都依赖于 pyrasite 所提供的交互式环境

```
# 连接进程，进入交互环境
root@ubuntu:~# pyrasite-shell 19460
Pyrasite Shell 2.0
Connected to 'python mock_high_memory_cycle.py'
Python 2.7.6 (default, Nov 23 2017, 15:49:48) 
[GCC 4.8.4] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(DistantInteractiveConsole)

>>>

# guppy 查看各种对象的内存占用情况
>>> from guppy import hpy
>>> h = hpy()
>>> h.heap()
Partition of a set of 372113 objects. Total size = 64189384 bytes.
 Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
     0  84828  23 23751840  37  23751840  37 dict of __main__.ObjectA
     1  84828  23 23751840  37  47503680  74 dict of __main__.ObjectB
     2  84828  23  5428992   8  52932672  82 __main__.ObjectA
     3  84828  23  5428992   8  58361664  91 __main__.ObjectB
     4    236   0  1608992   3  59970656  93 list
     5  14431   4  1183672   2  61154328  95 str
     6   7658   2   624584   1  61778912  96 tuple
     7    109   0   330040   1  62108952  97 dict of module
     8    272   0   286208   0  62395160  97 dict of type
     9    334   0   284368   0  62679528  98 dict (no owner)
<119 more rows. Type e.g. '_.more' to view.>

>>>
```

可以看到 `_main__.ObjectA` 和 `_main__.ObjectB` 的 `__dict__ ` 总共已经占用了 300 多 M 的内存了。找到了大内存占用对象，对应到源码中这两个对象的定义和其对应的逻辑语句，基本排除是单纯的大内存占用对象，那是不是违反垃圾回收机制导致的？这个需要进一步确定

```
# objgraph 查找违反垃圾回收机制的对象，并生成对象引用图
>>> import objgraph
>>> obj_a = ObjectA()
>>> obj_b = ObjectB()
>>> obj_a.__attr = obj_b
>>> obj_b.__attr = obj_a
>>> objgraph.show_refs([obj_a, obj_b], filename='report.png')
Graph written to /tmp/objgraph-rTkgLe.dot (27 nodes)
Image generated as report.png

>>>
```

4、对象引用图格式转换

```
# cd 到 /tmp 目录下

root@ubuntu:/tmp# ls
objgraph-rTkgLe.dot

root@ubuntu:/tmp# dot objgraph-rTkgLe.dot -Tpng -o report.png
Fontconfig warning: ignoring UTF-8: not a valid region tag

root@ubuntu:/tmp# ls
objgraph-rTkgLe.dot report.png
```

5、查看对象引用图

![](https://user-gold-cdn.xitu.io/2018/5/18/163724b396dd60af?w=3473&h=701&f=png&s=160723)

6、结论

发现存在循环引 ObjectA --> dict --> ObjectB --> dict --> ObjectA，且循环链上有两个有自定义的 `__del__` 方法

至此，案例一的内存占用问题已经排查完毕，结论是**因 ObjectA 和 ObjectB 存在循环引用，两个对象无法被垃圾回收，从而导致对内存占用的持续升高**

**案例二：存在单纯的大内存占用对象**

一个用于模拟创建单纯大内存对象的脚本 `mock_high_memory_pure.py`，内容如下：

```
# -*- coding=utf-8 -*-

import time


_pure_string = ''

# 持续执行，模拟让 str 占用的内存越来越大
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
    
    # 避免太快被 OOM 机制制裁，而无法观察
    time.sleep(0.0001)

```

运行 `mock_high_memory_pure.py` 等待 3 分钟，通过 `top` 已经可以看到进程的内存占用从一开始的 1.3% 飙升到 57.3%，可以开始排查

```
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                                          
20779 root      20   0   30476  13188   4424 S   7.3  1.3   0:00.22 python demo3.py
```

```
PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                                          
20779 root      20   0  598508 581116   4424 S  10.0 57.3   0:24.86 python demo3.py
```

排查步骤和案例一基本一致，重复的地方就不赘述了。首先用 `1、ps 定位进程中的高内存占用线程` 的方法定位进程中高内存占用的线程；然后用 `2、gdb 定位线程调用栈` 中确定线程正在执行的代码上下文；重点看下 `3、pyrasite 交互式调试` 步中 guppy 和 objgraph 的结果

```
root@ubuntu:~# pyrasite-shell 20779
Pyrasite Shell 2.0
Connected to 'python mock_high_memory_cycle.py'
Python 2.7.6 (default, Nov 23 2017, 15:49:48) 
[GCC 4.8.4] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(DistantInteractiveConsole)

>>>
>>> from guppy import hpy
>>> h = hpy()
>>> h.heap()
Partition of a set of 32494 objects. Total size = 480517536 bytes.
 Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
     0  14381  44 477531168  99 477531168  99 str
     1   7635  23   622816   0 478153984 100 tuple
     2    109   0   327736   0 478481720 100 dict of module
     3    258   1   280752   0 478762472 100 dict of type
     4   2112   6   270336   0 479032808 100 types.CodeType
     5    285   1   262968   0 479295776 100 dict (no owner)
     6   2046   6   245520   0 479541296 100 function
     7    258   1   230160   0 479771456 100 type
     8    140   0   154400   0 479925856 100 dict of class
     9   1109   3    88720   0 480014576 100 __builtin__.wrapper_descriptor
<112 more rows. Type e.g. '_.more' to view.>

# 可以看到存在一个占用了 400 多 M 内存的 str 对象
# 同案例一，我们需要通过对象图来进一步确认是哪种情况

>>>
>>> import objgraph
>>> objgraph.show_refs([_pure_string], filename='report02.png')

# 格式转换省略
```

对象图如下：

![](https://user-gold-cdn.xitu.io/2018/5/18/163729a1c979b2b6?w=331&h=61&f=png&s=3655)

可以很清楚地看到并没有循环引用，只是**单纯的大内存占用对象搞的鬼**

---

### <font color=#00b0f0>总结</font>

当然为了方便理解，上面的案例都是比较简单的，在实际的项目中，出现内存泄漏的不一定是我们自己写的代码，而有可能是一些第三方库。当遇到这种情况，就需要对第三方库进行单独的调试，也就是把第三方库 “当作” 我们自己写的代码，然后按照上面的排查步骤去调试
