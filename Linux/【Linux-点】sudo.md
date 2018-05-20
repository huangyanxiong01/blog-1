### <font color=#00b0f0>简介</font>

Linux 是一个多用户系统，不同用户之间有时候需要进行一些合理的越权操作，一般有两种方法：su 和 sudo，本文着重讨论 sudo。

关键字：**使用场景、/etc/sudoers 配置文件**

---

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

### <font color=#00b0f0>使用场景</font>

假设不知道 root 密码的普通用户 tiger 想要查看 `/etc/shadow` 文件的内容

```
tiger@Lab:/etc$ cat /etc/shadow
cat: /etc/shadow: Permission denied
```

发现提示对该文件没有操作权限，通过 `ls -l` 命令发现该文件的属主是 root，属组是 shadow，并且对其他属主和属组没有赋予任何权限

```
tiger@Lab:/etc$ ls -l /etc/shadow
-rw-r----- 1 root shadow 842 May  6 14:14 /etc/shadow
```

此时，可以利用 `sudo` 并输入 tiger 的密码来解决问题

```
tiger@Lab:/etc$ sudo cat /etc/shadow
[sudo] password for tiger:
root:$6$XGe/wN8w$D0CC0ARj5gCCPxTHb7JmzinCrQopCT6hp8BF7Hinp6hTKFxEOgbsdqyB9HLifahJq7R2fP8XmGnyHlM4JVL9L/:17657:0:99999:7:::
daemon:*:16484:0:99999:7:::
bin:*:16484:0:99999:7:::
sys:*:16484:0:99999:7:::
sync:*:16484:0:99999:7:::
games:*:16484:0:99999:7:::
... ...
```

> 可以看到，`sudo` 适用于实现越权操作

---

### <font color=#00b0f0>/etc/sudoers 配置文件</font>

#### 初识 /etc/sudoers

那么，上面为什么加了 `sudo` 就可以操作原来无法执行 `cat /etc/shadow` 呢？因为 `sudo` 命令的配置文件 `/etc/sudoers` 已经默认配置好了用户 tiger 和 `sudo` 相关的规则，文件内容如下：

```
# This file MUST be edited with the 'visudo' command as root.
#
# Please consider adding local content in /etc/sudoers.d/ instead of
# directly modifying this file.
#
# See the man page for details on how to write a sudoers file.
#
Defaults        env_reset
Defaults        mail_badpass
Defaults        secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Host alias specification

# User alias specification

# Cmnd alias specification

# User privilege specification
root    ALL=(ALL:ALL) ALL
%tiger ALL=(ALL:ALL) ALL

#includedir /etc/sudoers.d
```

重点是这里：`%tiger ALL=(ALL:ALL) ALL`。这条规则的意思是，当用户 tiger 无论在任何的主机上面执行 `sudo` 命令，都可以切换成任何用户的身份，去执行任何的命令（包括 root）。所以，用户 tiger 执行 `sudo` 之后能操作 root 的文件也就说得通了。

#### /etc/sudoers 详解

**基本语法**

- “#” 后的语句为注释
- 当一行规则太长时，可以用 “\” 进行续行

**文件内容详解**

配置文件分为别名定义和规则定义两部分，以一份较为完整的配置文件为例

```
User_Alias     OPERATORS = joe, mike, jude
Runas_Alias    OP = root, operator
Host_Alias     OFNET = 10.1.2.0/255.255.255.0
Cmnd_Alias     PRINTING = /usr/sbin/lpc, /usr/bin/lprm

OPERATORS ALL=ALL
linus ALL=(OP) ALL
user2 OFNET=(ALL) ALL
user3 ALL= PRINTING
go2linux ALL=(ALL) ALL
```

1、别名定义部分为：

```
User_Alias     OPERATORS = joe, mike, jude
Runas_Alias    OP = root, operator
Host_Alias     OFNET = 10.1.2.0/255.255.255.0
Cmnd_Alias     PRINTING = /usr/sbin/lpc, /usr/bin/lprm
```

别名定义的语法为：Alias_Type NAME = item1, item2,... 或者 Alias_Type NAME = item1, item2, item3:NAME = item4, item5,...

Alias_Type 支持四种类型：

- Host_Alias：定义主机别名
- User_Alias：定义用户，别名成员可以是用户，用户组（前面要加%号）
- Runas_Alias：定义目的用户，即 sudo 允许切换到的用户
- Cmnd_Alias：定义命令别名

NAME 就是别名，可以由字母、数字和下划线组成，但必须以大写首字母开头。比如 aBC、_ABC、0Bc 就是不合法的别名。

item 就是别名所包括的成员了。当 Alias_Type 为 Host_Alias 时，item 就是有效的主机名或主机 ip，可以通过 `w` 命令查看；当 Alias_Type 为 User_Alias 时，item 就是真实存在的用户，如 tiger；当 Alias_Type 为 Runas_Alias 时，item 也是真实存在的用户，如 root；当 Alias_Type 为 Cmnd_Alias 时，item 就是允许执行的命令，且必须是绝对路径的形式，如 /bin/ls。

2、规则定义部分为：

```
OPERATORS ALL=ALL
linus ALL=(OP) ALL
user2 OFNET=(ALL) ALL
user3 ALL= PRINTING
go2linux ALL=(ALL) ALL
```

授权用户 主机=命令，这三个要素是必须的，缺一不可，而 `(目的用户)` 是可选的，当目的用户没有时，那么默认就是 `(root)`。

---

### <font color=#00b0f0>实例解读</font>

```
%tiger ALL=/bin/chown,/bin/chmod
```

> tiger 用户可以在任何可连接的主机终端中，切换到 root 用户身份，执行 `/bin/chown` 和 `/bin/chmod` 命令。和 `tiger ALL=(root) /bin/chown,/bin/chmod` 是同一个效果。

```
%tiger ALL=(root) NOPASSWD: /bin/chown,/bin/chmod
```

> tiger 用户可以在任何可连接的主机终端中，切换到 root 用户身份，执行 `/bin/chown` 和 `/bin/chmod` 命令，并且在执行 `/bin/chown` 时 不用输入密码，但是在执行 `/bin/chmod` 要输入密码。`NOPASSWD:` 参数对于脚本编写非常有用，可以避免脚本中的交互操作。

```
%tiger ALL=(root) NOPASSWD: /bin/chown, NOPASSWD: /bin/chmod
```

> tiger 用户可以在任何可连接的主机终端中，切换到 root 用户身份，执行 `/bin/chown` 和 `/bin/chmod` 命令，并且在执行 `/bin/chown` 和 `/bin/chmod` 时都不用输入密码。

```
%tiger ALL=/usr/sbin/*,/sbin/*
```

> tiger 用户可以在任何可连接的主机终端中，切换到 root 用户身份，执行 `/usr/sbin/` 和 `/sbin/` 下的所有命令。

```
%tiger ALL=/usr/sbin/*,/sbin/*,!/usr/sbin/fdisk
```

> tiger 用户可以在任何可连接的主机终端中，切换到 root 用户身份，执行 `/usr/sbin/` 和 `/sbin/` 下的所有命令，但是不能执行 `/usr/sbin/fdisk` 命令。这种 `!` 语法常用于限制一些危险的命令，如 `!/usr/bin/passwd root` 来限制普通用户越权来修改 root 口令。

```
User_Alias USER=tiger,pig,dog 
Host_Alias HOST=10.1.2.0/24
Runas_Alias OP=bear
Cmnd_Alias CMD=/sbin/parted,/sbin/fdisk

USER HOST=(OP) CMD
```

> 用户 tiger、pig、dog 可以在网段为 10.1.2.0/24 的主机终端中，切换到 bear 用户身份，执行 `/sbin/parted` 和 `/sbin/fdisk` 命令。

---

### <font color=#00b0f0>不使用 vi </font>

在修改 `/etc/sudoers` 时，`visudo` 默认是使用 `vi` 来进行的。其实可以修改成我们习惯的编辑器，如：

- 使用 vim 修改 

```
export VISUAL=vim; visudo
```

- 使用 nano 修改

```
export VISUAL=nano; visudo
```

> 注意：上述 `export` 操作要在 root 状态下执行，因为修改 `/etc/sudoers` 必须是在 root 状态下进行。
