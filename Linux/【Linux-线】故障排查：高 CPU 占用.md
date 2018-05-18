### <font color=#00b0f0>热身：两个常见的 CPU 异常场景</font>

案例一：

```
top - 11:33:32 up 57 min,  4 users,  load average: 45, 44, 43
Tasks: 173 total,   1 running, 172 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.0 us,  0.0 sy,  0.0 ni,90.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem:   1014068 total,   370796 used,   643272 free,    43448 buffers
KiB Swap:        0 total,        0 used,        0 free.   201980 cached Mem

...
```

观察到 `load average` 和 `id` 指标都很高，这种情况一般都是存在状态为 D (disk sleep) 的进程，常见于同步等待 IO 事件 (磁盘 IO、网络 IO 等)。“D 进程” 不接受外来的任何信号，也就是无法被 kill，也无法自行结束，只能等待 IO 事件完成或者重启系统。

几种解决方法：

- 从 IO 事件入手：通过 `ps axjf | grep -w "D"` 来找出 D 进程 PID，确定等待的 IO 事件 (可以通过 `strace -p PID` 观察系统调用来辅助确定)，确保 IO 事件是可以完成的。
- 从 IO 模型入手：若 D 进程的代码是可控的，将 D 进程中的同步 IO 换成 异步 IO
- 简单粗暴非长久：重启系统

案例二：

内核进程 kswapd0 高 CPU 占用。kswapd0 是虚拟内存管理进程，当系统发现物理内存不够用时，就会唤醒 kswapd0 分配磁盘交换空间作为缓存，而该过程是非常消耗 CPU 资源的。

解决方法：

排查方向转向内存不足，这个又是另外一个专题，大致方向是排查是否存在异常的大内存进程、升级物理内存等。

### <font color=#00b0f0>造成高 CPU 占用的重要原因</font>
- **死循环 (循环条件)：实际情况一般是因为循环条件是关于某种等待，比如循环条件依赖同步 IO 读的结果成功，而同步 IO 读阻塞了，从而造成的死循环**
- **算法复杂度太大 (循环次数)：比如 3 个嵌套的 for 循环，且循环次数大**
- **循环语句依赖一些脆弱的外部系统 (循环语句)：比如在一个大循环中执行数据库操作**

### <font color=#00b0f0>排查步骤</font>

一个用于实验的 Python 脚本 mock_high_cpu.py，内容如下：

```
# -*- coding:utf-8 -*-

import threading
import time


# 线程1，模拟正常 CPU 占用
def worker_low_cpu():
    for i in range(5):
        print 'low cpu'
        time.sleep(2)
    return


# 线程2，模拟高 CPU 占用
def worker_high_cpu():
    while 1:
        print 'high cpu'


# 启动
t1 = threading.Thread(target=worker_low_cpu)
t2 = threading.Thread(target=worker_high_cpu)
t1.start()
t2.start()
t1.join()
t2.join()
```

执行 mock_high_cpu.py 并敲入 `top` 命令：

```
top - 15:43:47 up  5:07,  4 users,  load average: 0.60, 0.20, 0.37
Tasks: 178 total,   2 running, 176 sleeping,   0 stopped,   0 zombie
%Cpu(s): 23.5 us, 57.3 sy,  0.0 ni, 12.8 id,  0.0 wa,  0.4 hi,  6.0 si,  0.0 st
KiB Mem:   1014068 total,   430268 used,   583800 free,    51096 buffers
KiB Swap:        0 total,        0 used,        0 free.   238832 cached Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                                                                
 4753 root      20   0  171980   7264   4408 S  54.1  0.7   0:14.03 python mock_high_cpu.py
 
 ...
```

可以看到 `id`、`us`、`sy` 等 CPU 相关的指标都如期地发生变化，而且 `python mock_high_cpu.py` 进程的 CPU 占用率也达到 54.1。OK，我们已经成功地模拟了一个高 CPU 占用的进程，接下来可以开始排查了。

**1、找到 PID**

根据 `top` 命令我们很容易就找到了 PID 为 4753

**2、strace 查看系统调用**

执行 `strace -p 4753`，可以看到一个关于互斥的系统调用，如下：

```
root@ubuntu:/opt# strace -p 4753
Process 4753 attached
futex(0x1643800, FUTEX_WAIT_PRIVATE, 0, NULL
```

虽然这个例子的系统调用没有反应什么问题，不过对于故障排查来说，线索是不嫌多的，了解进程的系统调用往往可以帮助我们缩小问题的范围，也有了尝试定位问题的依据。

**3、由 PID 找到 TID**

执行 `ps -mp 4753 -o THREAD,tid,time` 如下：

```
root@ubuntu:/opt# ps -mp 4753 -o THREAD,tid,time
USER     %CPU PRI SCNT WCHAN  USER SYSTEM   TID     TIME
root     54.2   -    - -         -      -     - 00:00:06
root      0.0  19    - futex_    -      -  4753 00:00:00
root      0.0  19    - poll_s    -      -  4754 00:00:00
root     54.0  19    - -         -      -  4755 00:00:06
```

在进程 4753 中有两个线程，TID 分别是 4754 和 4755。其中，4754 的 CPU 占用率几乎可以忽略不计，而造成进程 4753 高 CPU 占用的罪魁祸首就是线程 4755。

看到这里，聪明的水友已经猜到了，4754 其实是执行 `worker_low_cpu` 函数的线程，而 4755 就是执行 `worker_high_cpu` 函数的线程，下面的一些调试结果也可以证明这一点。

**4、gdb 查看调用栈**

4.0、安装 gdb，执行

```
apt-get update -y
apt-get install -y gdb
```

4.1、执行 `gdb`，进入 gdb 交互界面

4.2、执行 `attach 4753` 连接上要调试的进程

4.3、执行 `info threads` 查看基本线程信息：

```
  Id   Target Id         Frame 
  2    Thread 0x7fc002d2b700 (LWP 4755) "python" 0x00007fc00420b3ad in write () at ../sysdeps/unix/syscall-template.S:81
* 1    Thread 0x7fc004914740 (LWP 4753) "python" sem_wait () at ../nptl/sysdeps/unix/sysv/linux/x86_64/sem_wait.S:85
```

`1` 前面的 `*` 号代表当前调试的是该线程。看到 `(LWP 4755)` 对应的线程标号是 2

4.4、执行 `thread 2` 切换到 4755 线程：

```
[Switching to thread 2 (Thread 0x7fc002d2b700 (LWP 4755))]
#0  0x00007fc00420b3ad in write () at ../sysdeps/unix/syscall-template.S:81
81  ../sysdeps/unix/syscall-template.S: No such file or directory.
(gdb) info threads 
  Id   Target Id         Frame 
* 2    Thread 0x7fc002d2b700 (LWP 4755) "python" 0x00007fc00420b3ad in write () at ../sysdeps/unix/syscall-template.S:81
  1    Thread 0x7fc004914740 (LWP 4753) "python" sem_wait () at ../nptl/sysdeps/unix/sysv/linux/x86_64/sem_wait.S:85
```

4.5、执行 `bt` 查看线程 4755 的调用栈：

```
#0  0x00007fc00420b3ad in write () at ../sysdeps/unix/syscall-template.S:81
#1  0x00007fc004194f13 in _IO_new_file_write (f=0x7fc0044df400 <_IO_2_1_stdout_>, data=0x7fc004922000, n=9) at fileops.c:1261
#2  0x00007fc0041963ec in new_do_write (to_do=9, data=0x7fc004922000 "high cpu\n\n", fp=0x7fc0044df400 <_IO_2_1_stdout_>) at fileops.c:538
#3  _IO_new_do_write (fp=0x7fc0044df400 <_IO_2_1_stdout_>, data=0x7fc004922000 "high cpu\n\n", to_do=9) at fileops.c:511
#4  0x00007fc0041955b1 in _IO_new_file_xsputn (f=0x7fc0044df400 <_IO_2_1_stdout_>, data=<optimized out>, n=1) at fileops.c:1332
#5  0x00007fc00418a6f4 in __GI__IO_fputs (str=str@entry=0x5faf00 "\n", fp=fp@entry=0x7fc0044df400 <_IO_2_1_stdout_>) at iofputs.c:40
#6  0x0000000000515441 in PyFile_WriteString (s=s@entry=0x5faf00 "\n", f=f@entry=<file at remote 0x7fc0048f6150>) at ../Objects/fileobject.c:2638
#7  0x00000000004cd967 in PyEval_EvalFrameEx (f=f@entry=Frame 0x7fc0047bf3a0, for file mock_high_cpu.py, line 14, in worker_high_cpu (), throwflag=throwflag@entry=0) at ../Python/ceval.c:1819
#8  0x00000000004704ea in PyEval_EvalCodeEx (closure=<optimized out>, defcount=<optimized out>, defs=0x0, kwcount=<optimized out>, kws=<optimized out>, argcount=<optimized out>, args=<optimized out>, locals=0x0, globals=<optimized out>, co=<optimized out>) at ../Python/ceval.c:3252

...
```

**重点找到 `for file XXX line XXX in XXX` 字样，也就是 `#7` 中的 `for file mock_high_cpu.py, line 18, in worker_high_cpu ()`**

根据这个提示可以在源码中找到对应的语句 `print 'high cpu'`，线程 4755 正在运行的是这行代码。根据 “**造成高 CPU 占用的重要原因**”        ，然后查看上下文发现该行代码处于一个死循环中。

### <font color=#00b0f0>更进一步</font>

Python 里面暂时还没有找到像 jstack 那么方便的调试工具，不过 gdb 也有一个还算好用的 Python 扩展。

安装方法：

```
apt-get install -y python-dbg
```

等安装完成之后，`cd` 到 mock_high_cpu.py 所在的目录。看到上面步骤 4.5，此时可以执行 `py-bt`，可以得到一个更容易看懂的调用栈，如下：

```
(gdb) py-bt
#7 Frame 0x7fc0047bf3a0, for file mock_high_cpu.py, line 14, in worker_high_cpu ()
    print 'high cpu'

...
```

还可以执行 `py-list` 得到线程 4755 正在执行哪一行的代码，如下：

```
(gdb) py-list
   9        return
  10    
  11    
  12    def worker_high_cpu():
  13        while 1:
 >14            print 'high cpu'
  15            #print 'demo4'
  16            pass
  17    
  18    
  19    threads = []
```

执行 `thread apply all py-list` 还可以同时查看所有线程分别在执行哪一行代码，如下：

```
(gdb) thread apply all py-list

Thread 2 (Thread 0x7fc002d2b700 (LWP 4755)):
   9        return
  10    
  11    
  12    def worker_high_cpu():
  13        while 1:
 >14            print 'high cpu'
  15            #print 'demo4'
  16            pass
  17    
  18    
  19    threads = []

Thread 1 (Thread 0x7fc004914740 (LWP 4753)):
 334            waiter.acquire()
 335            self.__waiters.append(waiter)
 336            saved_state = self._release_save()
 337            try:    # restore state no matter what (e.g., KeyboardInterrupt)
 338                if timeout is None:
>339                    waiter.acquire()
 340                    if __debug__:
 341                        self._note("%s.wait(): got it", self)
 342                else:
 343                    # Balancing act:  We can't afford a pure busy loop, so we
 344                    # have to sleep; but if we sleep the whole timeout time,
(gdb)
```

### <font color=#00b0f0>总结</font>

排查步骤：PID --> SYSCALL --> TID --> STACK --> SRC
