系统底层的事件都是由内核去处理的，正常来说对用户进程是透明的。但是用户空间的进程往往也需要知道某种类型的事件是否发生了，这个时候就需要有一种通信机制。Linux 中的信号就是内核提供给用户空间的一种通信接口。

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

### <font color=#00b0f0>常见信号</font>

| 编号     | 名称     | 代表事件  | 默认处理  | 发出者   |
|----------|----------|----------|----------|----------|
| 1 | SIGHUB | 终端挂断 | 终止 | 终端 |
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
| 19 | SIGSTOP | 停止进程直到接受到 SIGCONT 信号 | 停止 | 内核 |
