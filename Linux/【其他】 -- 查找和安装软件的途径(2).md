### <font color=#00b0f0>简介</font>

[查找和安装软件的途径(1)](https://juejin.im/post/5aebf69c6fb9a07a9f01699b)中讨论了如何查找，现在来探讨下如何安装的问题。

关键字：**deb 包、安装方式、编译安装、dpkg、apt-get、搭建私有镜像仓库、Docker**

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

### <font color=#00b0f0>deb 包</font>

在 Linux 下安装软件有两种方法：编译安装和包管理安装。由于编译安装对于普通的桌面用户来说并不是很友好，因为其涉及到各种依赖关系的处理。

因此，为了推广 Linux 系统，人们发明了另外一种方法。把预先编译好的软件包放到服务器上，让用户通过一条简单的命令就可以完成安装。这种方法就是包管理系统安装，编译好的软件包就是 deb 包。

> deb 软件包名规则：Package_Version-Build_Architecture.deb
>
>
> 例子：nano_1.3.10-2_i386.deb
> - 软件包名称 (Package Name): nano
> - 版本 (Version Number): 1.3.10
> - 修订号 (Build Number): 2
> - 平台 (Architecture): i386

---

### <font color=#00b0f0>安装方式</font>


- 编译安装

    ```
    # 下载源码
    wget src-name.tar.gz
    
    # 三板斧
    ./configure
    make
    make install
    ```

- dpkg

    ```
    # 下载 deb 包
    wget package-name.deb
    
    # 安装
    dpkg -i package-name.deb
    ```

- apt-get 
    ```
    # 更新软件包列表
    apt-get update -y
    
    # 安装
    apt-get install software-name
    ```

编译安装、dpkg、apt-get 三者的关系
- 都是用来安装软件的，但使用场景不同
- 易用性：编译安装 < dpkg < apt-get
- 使用频率：dpkg < 编译安装 < apt-get
- 定制：apt-get <= dpkg < 编译安装

---

### <font color=#00b0f0>编译安装</font>

编译安装最明显的好处就是可定制程度大，适合 geek，最大的缺点是人肉处理依赖关系。本文重点讨论包管理方式的安装，故暂时略过，有缘再探讨。

---

### <font color=#00b0f0>dpkg</font>

dpkg 是 Debian 的一个底层包管理工具，主要用于对已下载到本地和已安装的软件包进行管理。相比编译安装最大的好处是无需编译，直接安装即可。但是，人肉处理依赖关系的问题还在。

在日常的服务器维护中，一般情况下都不会直接使用该工具。

---

### <font color=#00b0f0>apt-get</font>

关于 dpkg 和 apt-get 两者的区别可以参考 [askubuntu](https://askubuntu.com/questions/309113/what-is-the-difference-between-dpkg-and-aptitude-apt-get) 上的一个回答：

```
No, dpkg only installs a package, so doing dpkg -i packageName.deb
will only install this Deb package, and will notify you of any
dependencies that need to be installed, but it will not install
them, and it will not configure the packageName.deb because
well...the dependencies are not there.

apt-get is a Package Management System that handles the
installation of Deb packages on Debian-based Linux distributions. A
Package Management System is a set of tools that will help you
install, remove, and change packages easily. So apt-get is like a
clever dpkg.
```

dpkg 仅仅是安装所指定的软件而已，如果在安装的过程中存在依赖，必须要手动去安装这些依赖包。而 apt-get 是智能版本的 dpkg，它会自动处理依赖关系，这一切都是透明的，是真正的一键安装。

#### apt-get 组成

广义的 apt-get 不单单是一个命令，而是指一个系统，包括：

- 服务端：源服务器/镜像服务器 (以 web、ftp 或其他网络服务的形式提供)
- 客户端
    - apt-get 配置文件
    - apt-get 命令本身

#### apt-get 配置文件

- `/etc/apt/sources.list`： 镜像服务器列表
    - 例子：
        ```
        deb http://mirrors.aliyuncs.com/ubuntu/ trusty main restricted universe multiverse
        deb-src http://mirrors.aliyuncs.com/ubuntu/ trusty main restricted universe multiverse
        ```
        按照一行一行来，每行可以分为四部分
        ```
        deb               URI地址                           版本代号     软件包分类
        deb/dev-src       mirrors.aliyuncs.com/ubuntu/     trusty      main restricted universe multiverse 
        ```
        **deb**：代表软件包是 deb 包形式
        
        **dev-src**：软件包是源码形式
        
        **mirrors.aliyuncs.com/ubuntu/**：镜像服务器的 URI
        
        **trusty**：软件包支持安装的发行版
        
        **main restricted universe multiverse**：软件包分类
        
        
        发行版分两类，发行版代号和发行版类型，其中发行版代号取值有 trusty、xenial、precise；发行版类型取值有 oldstable、stable、testing、unstable，分别代表 旧的稳定版本、稳定版本、测试版本、不稳定版本。不建议使用 testing 和 unstable 的源
        
        软件包分类的取值有 main、restricted、universe、multiverse，分别代表 官方支持的自由软件、官方支持的非完全自由软件、社区维护的自由软件、非自由软件
    
    - 皮一下：当把 /etc/apt/sources.list 清空后，还能正常使用 apt-get 吗？
        ```
        # 备份 /etc/apt/sources.list
        root@ubuntu:/etc/apt# ls
        apt.conf.d  preferences.d  sources.list  sources.list.d  sources.list.save  sources.list~  trusted.gpg  trusted.gpg.d  trusted.gpg~
        root@ubuntu:/etc/apt# cp -a sources.list sources.list.backup
        root@ubuntu:/etc/apt# ls
        apt.conf.d  preferences.d  sources.list  sources.list.backup  sources.list.d  sources.list.save  sources.list~  trusted.gpg  trusted.gpg.d  trusted.gpg~
        
        # 清空 /etc/apt/sources.list
        root@ubuntu:/etc/apt# echo '' > sources.list
        root@ubuntu:~# cat /etc/apt/sources.list
        
        root@ubuntu:~#
        
        # 卸载刚刚安装的 nginx
        略...
        
        # 安装 nginx
        root@ubuntu:/etc/apt# apt-get install nginx
        Reading package lists... Done
        Building dependency tree       
        Reading state information... Done
        Package nginx is not available, but is referred to by another package.
        This may mean that the package is missing, has been obsoleted, or
        is only available from another source
        However the following packages replace it:
            nginx-common
        
        E: Package 'nginx' has no installation candidate
        ```
        > 清空之后不能正常使用 apt-get

- `/var/lib/apt/lists`： 使用 `apt-get update` 命令会根据 `/etc/apt/sources.list` 为镜像服务器上所提供的软件包创建索引文件，并保存到该文件中，供 `apt-get install` 命令的使用

- `/var/cache/apt/archives`： 用 apt-get install 安装软件时，软件包的临时存放路径

- `/var/lib/dpkg/available`： 当前系统可用的的软件包列表
    - 例子：执行 `cat /var/lib/dpkg/available`，下面是其中一个可用软件包的详细信息 
        ```
        1 Package: libxml-libxml-perl
        2 Priority: optional
        3 Section: perl
        4 Installed-Size: 1003
        5 Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
        6 Architecture: amd64
        7 Version: 2.0108+dfsg-1ubuntu0.1
        8 Depends: libc6 (>= 2.14), libxml2 (>= 2.7.4), perl (>= 5.18.2-2ubuntu1), perlapi-5.18.2, libxml-namespacesupport-perl, libxml-sax-perl
        9 Size: 336770
       10 Description: Perl interface to the libxml2 library
       11  XML::LibXML is a Perl interface to the GNOME libxml2 library, which provides
       12  interfaces for parsing and manipulating XML files. This module allows Perl
       13  programmers to make use of the highly capable validating XML parser and the
       14  high performance Document Object Model (DOM) implementation. Additionally, it
       15  supports using the XML Path Language (XPath) to find and extract information.
       16 Homepage: https://metacpan.org/release/XML-LibXML/
       17 Original-Maintainer: Debian Perl Group <pkg-perl-maintainers@lists.alioth.debian.org>
       18 
        ```

    - 皮一下：当把 `/var/lib/dpkg/available` 清空后，还能正常使用 apt-get 吗？
        ```
        # 备份 /var/lib/dpkg/available
        root@ubuntu:/var/lib/dpkg# ls
        alternatives  available      cmethopt    diversions-old  lock   statoverride      status      triggers
        arch          available-old  diversions  info            parts  statoverride-old  status-old  updates
        root@ubuntu:/var/lib/dpkg# cp -a available available.backup
        root@ubuntu:/var/lib/dpkg# ls
        alternatives  available      available.backup  diversions      info  parts         statoverride-old  status-old  updates
        arch          available-old  cmethopt          diversions-old  lock  statoverride  status            triggers
        
        # 清空 /var/lib/dpkg/available
        root@ubuntu:/var/lib/dpkg# echo '' > available
        root@ubuntu:/var/lib/dpkg# cat available
        
        root@ubuntu:/var/lib/dpkg#
        
        # 安装 nginx 之前
        root@ubuntu:/var/lib/dpkg# which nginx
        root@ubuntu:/var/lib/dpkg#
        
        # 尝试安装 nginx
        root@ubuntu:/var/lib/dpkg# apt-get install nginx -y
        Reading package lists... Done
        Building dependency tree       
        ... ... 
        Setting up nginx-core (1.4.6-1ubuntu3.8) ...
        Setting up nginx (1.4.6-1ubuntu3.8) ...
        Processing triggers for libc-bin (2.19-0ubuntu6.5) ...
        root@ubuntu:/var/lib/dpkg#
        
        # 安装 nginx 成功
        root@ubuntu:/var/lib/dpkg# which nginx
        /usr/sbin/nginx
        root@ubuntu:/var/lib/dpkg#
        ```
    
        > 清空之后仍然能正常使用 `apt-get`，并且 `/var/lib/dpkg/available` 的内容更新为只有 nginx 软件包的详细信息

#### apt-get update 工作原理

- 执行 `apt-get update`
- 命令根据 `/etc/apt/sources.list` 所提供的镜像服务器列表，扫描每一个镜像服务器
- 为镜像服务器所提供的软件包资源建立索引文件，并保存在本地的 `/var/lib/apt/lists` 中；若软件包资源有更新，也会同步更新信息到本地索引文件

#### apt-get install 工作原理

- 扫描本地索引文件 `/var/lib/apt/lists`
- 检查软件包依赖，确定所有依赖包
- 确定了需要下载的依赖包，然后根据索引文件中的站点指示，到镜像服务器中下载
- 解压下载好的软件包，并自动完成安装和配置

#### apt-get 常用方式

- 安装 nginx

```
apt-get update -y
apt-get install nginx -y
```

- 彻底卸载 nginx

```
apt-get remove nginx -y
apt-get autoremove nginx -y
apt-get purge nginx -y
apt-get clean nginx -y
```

---

### <font color=#00b0f0>用 Docker 搭建私有镜像服务器</font>

既然广义的 apt-get 包含客户端和服务端两部分，那么服务端肯定也是要实践一下的。

#### 安装部署

- 执行 [deploy_repo.sh](https://github.com/oooooxooooo/pratice/blob/master/deb-repository/deploy_repo.sh) 脚本，一键部署镜像服务器
- 复制 [nginx.conf](https://github.com/oooooxooooo/pratice/blob/master/deb-repository/nginx.conf) 到 `/opt/nginx` 下 (*注意 tiger.japan.com 改成你的服务器域名*)
- 执行 [demo_pkg.sh](https://github.com/oooooxooooo/pratice/blob/master/deb-repository/demo_pkg.sh) 脚本，创建演示用的 deb 包
- 访问 http://tiger.japan.com/soft/ 可以看到很多的 deb 包

#### 测试镜像服务

- 备份 `/etc/apt/sources.list`
    ```
    root@ubuntu:/etc/apt# cp -a sources.list sources.list.backup
    ```

- 清空 `/etc/apt/sources.list`
    ```
    root@ubuntu:/etc/apt# echo '' > sources.list
    ```

- 把我们自己的镜像服务器地址写入 `/etc/apt/sources.list`
    ```
    # 注意 tiger.japan.com 改成你服务器的域名
    echo 'deb http://tiger.japan.com  soft/' > /etc/apt/sources.list
    ```

- 执行 `sudo apt-get update` 可以看到镜像服务器已经被使用
    ```
    root@ubuntu:/etc/apt# apt-get update
    Ign http://dl.google.com stable InRelease
    Hit http://dl.google.com stable Release.gpg                                    
    Hit http://dl.google.com stable Release                                        
    Hit http://dl.google.com stable/main amd64 Packages                            
    Ign http://tiger.japan.com soft/ InRelease                               
    Ign http://tiger.japan.com soft/ Release.gpg                             
    Ign http://tiger.japan.com soft/ Release                             
    Ign http://dl.google.com stable/main Translation-en                        
    Get:1 http://tiger.japan.com soft/ Packages [11.9 kB]                
    Ign http://tiger.japan.com soft/ Translation-en                          
    Hit https://download.docker.com trusty InRelease                           
    Hit http://ppa.launchpad.net trusty InRelease        
    Hit https://download.docker.com trusty/edge amd64 Packages                    
    Hit https://deb.nodesource.com trusty InRelease      
    Hit http://ppa.launchpad.net trusty InRelease     
    Hit https://packages.gitlab.com trusty InRelease                              
    Get:2 https://download.docker.com trusty/edge Translation-en                  
    Hit https://deb.nodesource.com trusty/main Sources                            
    Hit https://deb.nodesource.com trusty/main amd64 Packages                     
    Hit https://deb.nodesource.com trusty/main i386 Packages
    Get:3 https://deb.nodesource.com trusty/main Translation-en
    Hit https://packages.gitlab.com trusty InRelease                              
    Ign https://deb.nodesource.com trusty/main Translation-en                     
    Hit http://ppa.launchpad.net trusty/main amd64 Packages
    Hit https://packages.gitlab.com trusty/main Sources  
    Hit https://packages.gitlab.com trusty/main amd64 Packages
    Hit http://ppa.launchpad.net trusty/main i386 Packages
    Hit https://packages.gitlab.com trusty/main i386 Packages             
    Get:4 https://packages.gitlab.com trusty/main Translation-en
    Hit http://ppa.launchpad.net trusty/main Translation-en                     
    Hit https://packages.gitlab.com trusty/main Sources                         
    Hit https://packages.gitlab.com trusty/main amd64 Packages         
    Ign https://download.docker.com trusty/edge Translation-en                     
    Hit https://packages.gitlab.com trusty/main i386 Packages                  
    Hit http://ppa.launchpad.net trusty/main amd64 Packages                        
    Get:5 https://packages.gitlab.com trusty/main Translation-en                   
    Hit http://ppa.launchpad.net trusty/main i386 Packages                         
    Ign https://packages.gitlab.com trusty/main Translation-en                     
    Ign https://packages.gitlab.com trusty/main Translation-en                     
    Hit http://ppa.launchpad.net trusty/main Translation-en                        
    Fetched 11.9 kB in 8s (1438 B/s)                                               
    Reading package lists... Done
    root@ubuntu:/etc/apt#
    ```

---

### <font color=#00b0f0>总结</font>

感谢写出 apt-get 的大佬，感谢各种镜像服务器的维护者。🙏
