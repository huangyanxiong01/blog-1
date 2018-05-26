系统底层的事件都是由内核去处理的，正常来说对用户空间是透明的。但是用户空间的进程往往也需要知道某种类型的事件是否发生了，这个时候就需要有一种通信机制。信号就是一种通信接口，让内核进程和用户进程、用户进程和用户进程之间可以彼此沟通

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

### <font color=#00b0f0>了解信号</font>

#### 信号的产生

- 被动：当某种类型的事件发生了，被内核或者相应的驱动程序检测到，内核或者驱动程序就会向用户进程发送信号
- 主动：用户进程主动调用信号发送函数 (如 kill) 向另一个用户进程发送信号

#### 常见信号

| 编号     | 名称     | 代表事件  | 默认处理  | 产生   |
|----------|----------|----------|----------|----------|
| 1 | SIGHUP | 终端挂断 | 终止 | 终端 |
| 2 | SIGINT | 键盘中断 | 终止 | 键盘驱动 |
| 3 | SIGQUIT | 键盘退出 | 终止 | 键盘驱动 |
| 4 | SIGILL | 代码非法指令 | 终止 | 内核 |
| 9 | SIGKILL | 杀死进程 | 终止 | 内核 |
| 10 | SIGUSR1 | 用户定义的信号 1 | 终止 | 内核 |
| 12 | SIGUSR2 | 用户定义的信号 2 | 终止 | 内核 |
| 14 | SIGALRM | alarm 函数的定时器信号 | 终止 | 内核 |
| 15 | SIGTERM | /bin/kill 命令的默认信号 | 终止 | 内核 |
| 17 | SIGCHLD | 一个子进程的终结 | 忽略 | 内核 |
| 18 | SIGCONT | 继续被停止的进程 | 忽略 | 内核 |
| 19 | SIGSTOP | 停止进程直到接受到 SIGCONT 信号 | 停止/挂起 | 内核 |

> 进程对于信号的处理方式有 4 种：捕获、忽略、阻塞、默认；其中默认处理方式有 3 种：终止、忽略、挂起

- **SIGHUP**：在实际的工程实现中，这个信号更多时候是被守护进程重制用的，一般某个守护进程接收到该信号后，会先稳妥地关闭掉自己，然后以新的配置文件来重新启动。比如 nginx 中的 HUP 就是这种意思
- **SIGQUIT**：和 `SIGHUP` 类似，现实的工程实现中，这个信号往往会被用来稳妥地关闭自己。比如 nginx 中的 QUIT 信号
- **SIGINT**：当我们键入 `<Control-C>` 时，键盘驱动就会发出该信号
- **SIGTERM**：`kill` 命令的默认参数，和 `SIGKILL` 相比更像是请求进程退出
- **SIGKILL**：无法被**捕获**、**忽略**、**阻塞** 的信号，强制性进程退出，除僵尸进程外的其他进程都可以被这个信号杀掉
- **SIGSTOP**：无法被**捕获**、**忽略**、**阻塞** 的信号，被挂起的进程会一直等着 `SIGCONT` 信号的到来
- **SIGCONT**：无法被**阻塞**的信号

#### 验证 SIGKILL 和 SIGSTOP 的不可抗性

测试脚本如下：

```
# -*- coding=utf-8 -*-

import os
import signal


def handle_sigint(signum, frame):
    # 处理 SIGINT 信号
    print('handle signal SIGINT --> {}'.format(signum))
    print(frame)


def handle_sigstop(signum, frame):
    # 处理 SIGSTOP 信号
    print('handle signal SIGSTOP --> {}'.format(signum))
    print(frame)


def handle_sigkill(signum, frame):
    # 处理 SIGKILL 信号
    print('handle signal SIGKILL --> {}'.format(signum))
    print(frame)


def main():
    # 捕获 SIGINT 信号
    signal.signal(signal.SIGINT, handle_sigint)
    # 由于 SIGSTOP 和 SIGKILL 是不可抗的，如果这里注册了捕获运行时将会报 RuntimeError 异常
    pass

    # 发送 SIGINT 信号
    os.kill(os.getpid(), signal.SIGINT)
    # 发送 SIGSTOP 信号
    os.kill(os.getpid(), signal.SIGSTOP)
    # 发送 SIGSTOP 信号
    os.kill(os.getpid(), signal.SIGKILL)
    

if __name__ == '__main__':
    main()

```

运行脚本，发现 `SIGINT` 被捕获了，并且按照我们自定义的处理函数 `handle_sigint` 去处理了这个信号。但是 `SIGSTOP` 却不能被捕获，进程依然是被挂起了，这也导致了后面的 `SIGKILL` 没能发送出来。结果如下：

```
root@ubuntu:/opt# python signal01.py 
handle signal SIGINT --> 2
<frame object at 0x7f880c5e9050>

[1]+  Stopped                 python signal01.py
```

接着注释掉代码 `os.kill(os.getpid(), signal.SIGSTOP)` 再此执行脚本，`SIGINT` 仍然是顺利捕获，`SIGKILL` 跟 `SIGSTOP` 一样没能被捕获，该 kill 的还是被 kill 了。结果如下：

```
root@ubuntu:/opt# python signal01.py 
handle signal SIGINT --> 2
<frame object at 0x7fb85c389050>
Killed
```

---

### <font color=#00b0f0>发送信号</font>

常用的发送信号的方法有以下几种：

- 调用系统函数 kill
- 调用系统函数 alarm
- 从键盘发送信号 `<Control-C>`, `<Control-D>` 等
- 用 `/bin/kill` 程序

使用频率最高的应该是用 `/bin/kill` 程序发送信号了，但是这里有一个很容易被忽略的问题，先看下下面的脚本：

```
# -*- coding=utf-8 -*-

import os
import time


def child():
    # 被子进程调用
    print('I am child')
    # 循环不退出
    while 1:
        time.sleep(0.5)


def parent():
    # fork 子进程
    try:
        pid = os.fork()
    except OSError:
        exit("Could not create a child")

    if pid == 0:
        # 在子进程中，调用 child() 函数
        child()
    
    # 循环不退出
    while 1:
        time.sleep(0.5)

    # finished = os.waitpid(0, 0)
    # print(finished)


def main():
    parent()


if __name__ == '__main__':
    main()

```

执行脚本可以看到进程 fork 成功，且父进程是 `27242`，子进程是 `27243`，结果如下：

```
root@ubuntu:/tmp# ps axu | grep signal02.py | grep -v color
root     27242  0.0  0.6  24256  6972 pts/6    S+   19:51   0:00 python signal02.py
root     27243  0.0  0.4  24260  4712 pts/6    S+   19:51   0:00 python signal02.py
root@ubuntu:/tmp# ps -f 27243
UID        PID  PPID  C STIME TTY      STAT   TIME CMD
root     27243 27242  0 19:51 pts/6    S+     0:00 python signal02.py
```

此时，执行 `kill -9 27242` 会发现父进程被 kill 掉了，但是子进程还在，如下：

```
root@ubuntu:/tmp# kill -9 27242
root@ubuntu:/tmp# ps axu | grep signal02.py | grep -v color
root     27243  0.0  0.4  24260  4712 pts/6    S    19:51   0:00 python signal02.py
```

因为 `kill -9 27242` 只会 kill 当前的进程 (根本原因是 `/bin/kill` 程序对应的系统函数 kill 的 pid 参数正负影响着 kill 的执行结果)，而不会把当前进程的子进程也 kill 掉。如果想连当前进程的子进程都 kill 了，就要执行 `kill -9 -27242`。如下 (换了两个父子进程)：

```
root@ubuntu:/tmp# ps axu | grep signal02.py | grep -v color
root     27315  0.2  0.6  24256  6972 pts/6    S+   19:59   0:00 python signal02.py
root     27316  0.0  0.4  24260  4740 pts/6    S+   19:59   0:00 python signal02.py
root@ubuntu:/tmp# ps -f 27316
UID        PID  PPID  C STIME TTY      STAT   TIME CMD
root     27316 27315  0 19:59 pts/6    S+     0:00 python signal02.py
root@ubuntu:/tmp# kill -9 -27315
root@ubuntu:/tmp# ps axu | grep signal02.py | grep -v color
root@ubuntu:/tmp#
```

同时还有一个有意思的结果需要注意下，在 kill 掉父进程后，子进程并没有变成僵尸进程，而是被 init 进程收养了。如下：

```
root@ubuntu:/tmp# ps axu | grep signal02.py | grep -v color
root     27353  0.0  0.6  24256  6944 pts/6    S+   20:03   0:00 python signal02.py
root     27354  0.0  0.4  24260  4636 pts/6    S+   20:03   0:00 python signal02.py
root@ubuntu:/tmp# ps -f 27354
UID        PID  PPID  C STIME TTY      STAT   TIME CMD
root     27354 27353  0 20:03 pts/6    S+     0:00 python signal02.py
root@ubuntu:/tmp# kill -9 27353
root@ubuntu:/tmp# ps -f 27354
UID        PID  PPID  C STIME TTY      STAT   TIME CMD
root     27354     1  0 20:03 pts/6    S      0:00 python signal02.py
root@ubuntu:/tmp#
```

---

### <font color=#00b0f0>接收信号</font>

信号的处理流程大概如下图：

![](https://raw.githubusercontent.com/oooooxooooo/picture/master/Screen%20Shot%202018-05-22%20at%2010.18.33%20PM.png)

可以看到，信号的处理有 4 种方式，分别是捕获、忽略、默认处理、阻塞，前三种都比较好理解，重点看下阻塞

阻塞的意思是：假设 x0, x1, x2, x3, x4 是同一种信号。当进程正在处理信号 x0 的时候，来了一个信号 x1，内核会将 x1 标记为**待处理信号**；过一会儿来了信号 x2，此时内核开始阻塞这种信号，直接将 x2 丢掉；同理当 x3 来到时也会被丢弃。直到 x0 被处理完毕，内核才解除这种阻塞，然后把 x1 从待处理信号变成正在被处理的信号，这时如果来了 x4，x4 就会被标记成待处理信号。同时，`SIGKILL`, `SIGSTOP`, `SIGCONT` 这三个信号是不能被阻塞的

在《深入理解操作系统》第 537 页的图 8-36 有一个示例代码，演示的是由于**待处理信号之外的信号是不排队的**，这个特性会影响着信号处理的编码难度。比如，父进程的多个子进程几乎同时结束，这意味者父进程会在极短时间内接收到多个 `SIGCHLD` 信号，根据上面的解析可以知道，正常来说父进程是会部分丢弃该信号的，当父进程中的信号处理做得不完善时，就很容易导致僵尸进程的出现。但是，我用下面的程序却模拟不出来僵尸进程的结果，不知道是现在内核优化了，还是硬件配置高了，抑或是 Python 解析器帮我善后了，找个时间再用 Clang 来实验一下。代码如下：

```
import os
import signal
import time


def handle_sigchld(signum, frame):
    finished = os.waitpid(os.getpid(), 0)
    print(finished)
    time.sleep(3)


def parent():
    for i in range(5):
        try:
            pid = os.fork()
        except OSError:
            exit("Could not create a child")

    if pid == 0:
        print 'I am child'

    while 1:
        time.sleep(0.5)


def main():
    parent()


if __name__ == '__main__':
    main()

```
