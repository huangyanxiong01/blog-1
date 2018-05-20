### <font color=#00b0f0>简介</font>

对于开机操作都是点击一下控制面板按钮的事，好像人人都会。但是，这中间到底经历过的步骤个人认为还是要有一个认识的。

关键字：**引导、bootloader、执行启动脚本方式、运行级别、init、upstart**

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

### <font color=#00b0f0>引导</font>

对于服务器的开机操作，有个更加专业的名次 ---- 引导。

其实引导这个词非常贴切，因为从用户按下开机按钮开始，是靠一系列的连续且前后依赖的步骤组成的，就像是程序一步步引导着用户，直到最终用户可以顺利使用操作系统。

#### 引导过程

1. ROM 通电，启动 bootloader
2. bootloader 加载并启动 kernel
3. kernel 检查硬件
4. krenel 创建 init 进程
5. 管理员进入维护模式 (可选)
6. init 进程执行启动脚本

一般来说，我们最能掌控的就是第 6 点了。

#### 故障排查

引导过程可以类比网络中的 OSI 模型，其中 1 是最底层，依次递增。既然可以通过 OSI 模型来排查网络问题，那么，我们也可以通过引导过程来排查相关的引导问题。

*注意：下面的分析假设服务器硬件本身正常，也就是默认第 3 点正确。*

对于网络问题来说，故障排查最高效的方法是从底层到高层。因为底层问题往往是显而易见的，排查成本也是比较低的。例如 RJ45 端口的指示灯不亮了，就是明显的物理层问题。而对于引导的故障排查来说，也是遵循这样的原则。下面按照这种原则和通过几个问题来看下如何进行引导的故障排查。

#### 问题：系统镜像是否“干净”？

影响引导过程中的第 1、2、4 点。

因为系统镜像本身包括 bootloader、kernel 等核心组件，系统镜像可用很大程度上保证了引导的正常。因此，首先要确保所安装的系统是干净可用的，要到官方网站去下载系统镜像，例如 [ubuntu server 的官方下载点](https://www.ubuntu.com/download/server) 。

#### 问题：服务器硬件资源是否足够？

影响引导过程中的第 2 点中的启动。

因为 kernel 的一些内部数据结构的大小是静态确定的，在其启动的时，它会为自己划分出一块固定大小的内存空间，这块内存是 kernel 专用的，用户空间的进程无法使用。当服务器的内存小于 kernel 所需的内存时，将会造成内核启动失败。以 Ubuntu Server 为例，其所需的基础硬件资源如下：

- 300 MHz x86 processor
- 256 MiB of system memory (RAM)
- 1.5 GB of disk space


#### 问题：都执行了哪些启动脚本？

影响引导过程中的第 6 点。

当系统默认的启动脚本被错误修改，或者是执行了有问题的用户自定义脚本，都有可能会造成引导的失败。可以通过进入维护模式去查看修正有问题的脚本。ubuntu 进入维护模式方法如下：
```
1. 重启ubuntu，随即长按shirft进入grub菜单，或等待grub菜单的出现
2. 选择recovery mode，接着用方向键将光标移至recovery mode，按"e"键进入编辑页面
3. 将 ro recovery nomodeset 改为 rw single init=/bin/bash
4. 按 ctrl+x或者F10 进入单用户模式，当前用户即为root。这时候可以修改文件。修改完毕后重启即可
```

> 小结：通过上述几个问题，可以进行快速的引导故障排查和解决。

---

### <font color=#00b0f0>执行启动脚本方式</font>

当 1～4 步骤都没问题且管理员没有选择进入维护模式，init 主进程将会执行一些列的启动脚本，这些脚本之间会存在一定的依赖关系。init 和 upstart 两种常见的处理启动脚本的方式，两种方式都有运行级别的概念。

#### 运行级别

常见的 Linux 运行级别有 7 个，分别代表了不同的系统状态：关机模式、维护模式、多用户联网模式、图形界面联网模式、重引导模式。可以通过 `runlevel` 查看当前的运行级别。
```
┌─────────┬───────────────────┐
│Runlevel │ Target            │
├─────────┼───────────────────┤
│0        │ poweroff.target   │
├─────────┼───────────────────┤
│1        │ rescue.target     │
├─────────┼───────────────────┤
│2, 3, 4  │ multi-user.target │
├─────────┼───────────────────┤
│5        │ graphical.target  │
├─────────┼───────────────────┤
│6        │ reboot.target     │
└─────────┴───────────────────┘
```

我们熟悉的关机操作 `init 0` 其实就是将系统的运行级别切换成关机模式，从未达到关机的目的。同理，还可以通过 `init` 将系统切换到其他的运行级别。

#### init 关键目录和文件

- `/etc/init.d`：启动脚本的存放点
```
root@ubuntu:/etc/init.d# ls
README    console-setup     dns-clean          ipvsadm     networking  prl-x11    rcS           rsyslog         ssh       umountnfs.sh
acpid     cron              docker             irqbalance  nginx       prltoolsd  reboot        screen-cleanup  sudo      umountroot
apparmor  cryptdisks        friendly-recovery  keepalived  ondemand    procps     redis-server  sendsigs        sysstat   unattended-upgrades
apport    cryptdisks-early  grub-common        killprocs   postfix     rc         resolvconf    single          udev      urandom
atd       dbus              halt               kmod        pppd-dns    rc.local   rsync         skeleton        umountfs  x11-common
```

- `/etc/rc0.d、/etc/rc1.d、/etc/rc2.d、/etc/rc3.d、/etc/rc4.d、 /etc/rc5.d、/etc/rc6.d、/etc/rcS.d`：存放的脚本是 `/etc/init.d` 的软连接，按照一定的命名规范。每个目录对应一个运行级别，当系统运行级别发生改变时，系统将会到对应的 `/etc/rc*.d` 目录下执行启动脚本，而不是到 `/etc/init.d` 查找。下面以 `/etc/rc0.d` 为例。
```
root@ubuntu:/etc/rc0.d# ll
total 12
drwxr-xr-x   2 root root 4096 May  2 02:24 ./
drwxr-xr-x 118 root root 4096 May  2 12:52 ../
lrwxrwxrwx   1 root root   19 Aug  3  2017 K00prltoolsd -> ../init.d/prltoolsd*
lrwxrwxrwx   1 root root   29 Aug  3  2017 K10unattended-upgrades -> ../init.d/unattended-upgrades*
lrwxrwxrwx   1 root root   17 Sep 28  2017 K20ipvsadm -> ../init.d/ipvsadm*
lrwxrwxrwx   1 root root   20 Sep 28  2017 K20keepalived -> ../init.d/keepalived*
lrwxrwxrwx   1 root root   15 May  2 02:24 K20nginx -> ../init.d/nginx*
lrwxrwxrwx   1 root root   17 Feb 25 04:48 K20postfix -> ../init.d/postfix*
lrwxrwxrwx   1 root root   22 Nov  3 15:07 K20redis-server -> ../init.d/redis-server*
lrwxrwxrwx   1 root root   15 Aug  3  2017 K20rsync -> ../init.d/rsync*
lrwxrwxrwx   1 root root   24 Aug  3  2017 K20screen-cleanup -> ../init.d/screen-cleanup*
-rw-r--r--   1 root root  353 Mar 13  2014 README
lrwxrwxrwx   1 root root   18 Aug  3  2017 S20sendsigs -> ../init.d/sendsigs*
lrwxrwxrwx   1 root root   17 Aug  3  2017 S30urandom -> ../init.d/urandom*
lrwxrwxrwx   1 root root   22 Aug  3  2017 S31umountnfs.sh -> ../init.d/umountnfs.sh*
lrwxrwxrwx   1 root root   18 Aug  3  2017 S40umountfs -> ../init.d/umountfs*
lrwxrwxrwx   1 root root   26 Aug  3  2017 S59cryptdisks-early -> ../init.d/cryptdisks-early*
lrwxrwxrwx   1 root root   20 Aug  3  2017 S60umountroot -> ../init.d/umountroot*
lrwxrwxrwx   1 root root   14 Aug  3  2017 S90halt -> ../init.d/halt*
```

软连接的命名规范为：K 或 S + 数字 + 脚本所控制的服务名。其中，K 是 kill 的意思；S 是 start 的意思；数字就是执行优先级。

目的：通过这种命名规范，在发生运行级别切换时，可以细粒度地控制应该执行哪些脚本，按什么顺序执行 (因为脚本之间有依赖关系，例如先执行 ssh 服务的脚本，在执行 networking 服务的脚本就没有意义了)。

#### 工作过程

> 运行级别从低到高切换，例如 1 到 2

- init 查找 `/etc/rc2.d` 下的启动脚本
- init 按照脚本名字中的数字大小递增的顺序，带着 start 参数，依次执行 S 开头的脚本

> 运行级别从高到低切换，例如 2 到 0

- init 查找 `/etc/rc0.d` 下的启动脚本
- init 按照脚本名字中的数字大小递减的顺序，带着 stop 参数，依次执行 K 开头的脚本

因此，当引导到了第 6 点时，系统会得到一个默认的运行级别，一般是 2，此时就会按照规则去执行 `/etc/rc2.d` 下的脚本。

#### upstart

upstart 是比 init 更新的执行启动脚本的方式。虽然它保持了 init 运行级别的概念，但是依赖的目录变成了 `/etc/init`。

#### 为什么说 upstart 比 init 快？

和 init 方式相比，upstart 相比 init 的性能更好，因为 init 是以串行方式执行脚本，而 upstart 是以并行方式执行脚本的。

例如，运行级别从 1 到 2 时，需要执行 S10sshd 和 S20nginx 两个服务。但是，这两个服务并没有依赖关系。此时，init 还是会按照先 S10sshd 再 S20nginx 的顺序去执行；而 upstart 会同时执行 S10sshd 和 S20nginx。这一来一回就造成了两者性能的差距了。

#### upstart 实战

> 添加启动服务

1. 将你的启动脚本复制到 `/etc/init.d` 目录下，假设脚本文件名为 `test`
2. 设置脚本文件的权限 `sudo chmod 755 /etc/init.d/test`
3. 执行如下命令将脚本放到启动脚本中去
    ```
    cd /etc/init.d
    sudo update-rc.d test defaults 95
    ```
4. 该命令的输出信息参考如下
    ```
    update-rc.d: warning: /etc/init.d/test missing LSB information
    update-rc.d: see <http://wiki.debian.org/LSBInitScripts>
      Adding system startup for /etc/init.d/test ...
        /etc/rc0.d/K95test -> ../init.d/test
        /etc/rc1.d/K95test -> ../init.d/test
        /etc/rc6.d/K95test -> ../init.d/test
        /etc/rc2.d/S95test -> ../init.d/test
        /etc/rc3.d/S95test -> ../init.d/test
        /etc/rc4.d/S95test -> ../init.d/test
        /etc/rc5.d/S95test -> ../init.d/test
    ```

> 卸载启动服务

1. 执行
    ```
    cd /etc/init.d
    sudo update-rc.d -f test remove
    ```
2. 该命令的输出信息参考如下
    ```
    Removing any system startup links for /etc/init.d/test ...
        /etc/rc0.d/K95test
        /etc/rc1.d/K95test
        /etc/rc2.d/S95test
        /etc/rc3.d/S95test
        /etc/rc4.d/S95test
        /etc/rc5.d/S95test
        /etc/rc6.d/K95test
    ```

---

### <font color=#00b0f0>总结</font>

以上这些点都是是比较简单实用的，而引导更深层次的探讨就要涉及到内核和驱动方面的知识了。
