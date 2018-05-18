### <font color=#00b0f0>简介</font>

在服务器的日常管理中，有一个出现频率非常高的需求：“某个软件安装了没有，装在哪里了？” 注意，这里的软件泛指可执行的文件，比如系统自带的 `ls`，用户安装的 `nginx` 等。

当然，强大的 `find` 命令几乎可以解决 Linux 下所有的查找问题，但却有点杀鸡用牛刀的感觉。本文将重点探讨 `$PATH`、`which`、`whereis` 这些和软件查找相关的命令。

关键字：**查找软件、$PATH、which、whereis**

### <font color=#00b0f0>实验环境</font>
- 系统版本 Ubuntu 14.04
- 内核版本 3.16.0-30-generic
- 试验用的文件如下：

```
root@ubuntu:/usr/local/bin# pwd
/usr/local/bin
root@ubuntu:/usr/local/bin# ll ./testing.sh 
-rwxr-xr-x 1 root root 20 May  1 17:09 ./testing.sh*
```

```
root@ubuntu:/usr/sbin# pwd
/usr/sbin
root@ubuntu:/usr/sbin# ll testing.sh 
-rwxr-xr-x 1 root root 20 May  1 17:10 testing.sh*
```

```
root@ubuntu:/usr/games# pwd
/usr/games
root@ubuntu:/usr/games# ll testing 
lrwxrwxrwx 1 root root 15 May  1 18:11 testing -> /usr/bin/docker*
```

```
root@ubuntu:/opt# pwd
/opt
root@ubuntu:/opt# ll demo 
-rwxr-xr-x 1 root root 0 May  1 19:17 demo*
```

- `$PATH` 变量如下

```
root@ubuntu:~# echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/jvm/java-8-oracle/bin:/usr/lib/jvm/java-8-oracle/db/bin:/usr/lib/jvm/java-8-oracle/jre/bin
```

### <font color=#00b0f0>$PATH 变量</font>

在探讨 `which` 和 `whereis` 之前有必要先看一下 `$PATH`。Linux 有众多的系统环境变量，`$PATH` 就是其中一个。

对于该变量需要清楚以下几点：

- 组成：
    - `$PATH` 的值是一连串由 `:` 分割的目录组成
    - `which` 和 `whereis` 命令就是根据这些目录进行查找
    - `$PATH` 目录的顺序会影响 `which` 的查找结果，如果有两个同名的软件，则优先以靠前的目录作为结果

- 修改：和修改一般的 SHELL 变量一样

```
root@ubuntu:~# echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/jvm/java-8-oracle/bin:/usr/lib/jvm/java-8-oracle/db/bin:/usr/lib/jvm/java-8-oracle/jre/bin
root@ubuntu:~# PATH=$PATH:/opt
root@ubuntu:~# echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/jvm/java-8-oracle/bin:/usr/lib/jvm/java-8-oracle/db/bin:/usr/lib/jvm/java-8-oracle/jre/bin:/opt
```

### <font color=#00b0f0>which 命令</font>

`man which` 一下：

```
WHICH(1)                                                         General Commands Manual                                                        WHICH(1)

NAME
       which - locate a command

SYNOPSIS
       which [-a] filename ...

DESCRIPTION
       which  returns the pathnames of the files (or links) which would be executed in the current environment, had its arguments been given as commands
       in a strictly POSIX-conformant shell.  It does this by searching the PATH for executable files matching the names of the arguments. It  does  not
       follow symbolic links.

OPTIONS
       -a     print all matching pathnames of each argument

EXIT STATUS
       0      if all specified commands are found and executable

       1      if one or more specified commands is nonexistent or not executable

       2      if an invalid option is specified

Debian                                                                 1 May 2009                                                               WHICH(1)
```

举例子解析 man 信息：

- `which` 命令会根据当前 `$PATH` 变量的值，返回匹配到的绝对路径

    - 例子1：testing 既是可执行文件，其路径又在 `$PATH`
    的值中，故返回匹配结果
    
        ```
        root@ubuntu:~# pwd
        /root
        root@ubuntu:~# which testing
        /usr/games/testing
        ```

    - 例子2：demo 是可执行文件，但是其路径不在 `$PATH` 的值中，故无匹配结果

        ```
        root@ubuntu:~# pwd
        /root
        root@ubuntu:~# which demo
        root@ubuntu:~#
        ```


- `which` 命令会按照 `$PATH` 中目录的顺序进行查找，若不同目录下有同名的软件，则优先返回靠前的那个目录路径

    - 例子：`/usr/local/bin` 和 `/usr/sbin` 目录下都有 `testing.sh` 文件，但是由于 `/usr/local/bin` 在 `$PATH` 中的位置比 `/usr/sbin` 要靠前，则 `which testing.sh` 返回的是 `/usr/local/bin/testing.sh`
    
        ```
        root@ubuntu:~# which testing.sh 
        /usr/local/bin/testing.sh
        root@ubuntu:~#
        ```

- `which` 命令并不会区分符号连接
    - 例子：`testing` 是一个软连接，同样会被匹配到
        ```
        root@ubuntu:~# pwd
        /root
        root@ubuntu:~# which testing
        /usr/games/testing
        ```

- 若查找到对应的结果则该命令返回 0
    
    - 例子：匹配成功
    
        ```
        root@ubuntu:~# which testing.sh 
        /usr/local/bin/testing.sh
        root@ubuntu:~# echo $?
        0
        root@ubuntu:~#
        ```

- 若查找不到结果则该命令返回 1

    - 例子：匹配失败
    
        ```
        root@ubuntu:~# which demo
        root@ubuntu:~# echo $?
        1
        root@ubuntu:~#
        ```

- 若所带的参数有误则该命令返回 2
    
    - 例子：错误参数
    
        ```
        root@ubuntu:~# which -f testing.sh
        Illegal option -f
        Usage: /usr/bin/which [-a] args
        root@ubuntu:~# echo $?
        2
        root@ubuntu:~#
        ```

### <font color=#00b0f0>whereis 命令</font>

在查找二进制可执行文件方面，`which` 只会返回第一个匹配的绝对路径，`whereis` 则会返回所有匹配的绝对路径

- 例子：

        ```
        root@ubuntu:~# pwd
        /root
        root@ubuntu:~# which testing.sh
        /usr/local/bin/testing.sh
        root@ubuntu:~# whereis testing.sh
        testing: /usr/sbin/testing.sh /usr/games/testing /usr/local/bin/testing.sh
        root@ubuntu:~#
        ```

和 `which` 命令相比，除了可以查找二进制可执行文件外，`whereis` 还可以查找软件对应的源码（例：`whereis -s nginx`）和帮助手册（例：`whereis -m nginx`）。
