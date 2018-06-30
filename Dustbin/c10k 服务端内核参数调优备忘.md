# <font color=#42b983>#</font> TCP 内核参数

- net.ipv4.tcp_mem
    - 描述：内核 tcp 协议栈所能使用的总内存大小，单位页
    - 优化值：CxxxK 并发下总 socket 页数量 / 系统页大小 (一般 4k)

- net.ipv4.tcp_rmem 和 net.ipv4_tcp_wmem
    - 描述：单个 socket 的读和写缓存 (太小导致网络读写频繁；太大导致内存负载高)
    - 优化值：873200 1746400 3492800

- net.core.somaxconn 和 net.ipv4.tcp_max_syn_backlog
    - 描述：listen 监听的的队列长度 (当有 2 个连接到来时，服务端是先跟第一个连接做完 3 次握手，让第一个连接处于 ESTABLISHED 后，再开始和第二个连接进行 3 次握手。所以当队列长度太小而且连接太多时，服务端会丢弃来不及处理的连接，不跟它握手)
    - 优化值：8192/16384/32768 和 16384/32768/65535

- net.core.netdev_max_backlog
    - 描述：网卡接收队列。也就是当网卡的接收单个连接的速率比内核处理单个连接（3次握手）的速率快时，允许队列中数据包的最大数量 (应该要大于等于上述两个队列，因为它是物理层最先接触数据包，这里都丢弃了，上层的队列再大也没用)
    - 优化值：16384/32768/65535

- net.ipv4.tcp_max_orphans
    - 描述：假如孤儿 socket 超过所设置的值，则立即对这些孤儿 socket 发出 reset 包
    - 优化值：8192

- net.ipv4.tcp_keepalive_time
    - 描述：当连接处于 keepalive 时，服务端发送探测包的周期
    - 优化值：1800/1200

- net.ipv4.tcp_window_scaling
    - 描述：控制滑动窗口是否可变
    - 优化值：1

- (PS: 下面几个值特别适用于爬虫服务器)

- net.ipv4.tcp_fin_timeout = 30
    - 描述：对于本端发起的 socket 关闭，保持在 FIN_WAIT_2 状态的时间
    - 优化值：30

- net.ipv4.tcp_sack
    - 描述：选择性地应答乱序的tcp包（会增加cpu负载）
    - 优化值：1

- net.ipv4.tcp_tw_recycle 和 net.ipv4.tcp_tw_reuse
    - 描述：快速回收和重用 TIME_WAIT 状态的 socket 连接
    - 优化值：1 和 1

- net.ipv4.ip_local_port_range
    - 描述：本端作为客户端时可以发起更多的连接
    - 优化值：1024 65535

# <font color=#42b983>#</font> 文件描述符内核参数

- 系统级调整
    - 内核能打开的文件描述符最大数量
        - 例子：echo "fs.file-max=1100000" >> /etc/sysctl.conf
    - 进程能打开的文件描述符最大数量
        - 例子：echo "fs.nr_open=1100000" >> /etc/sysctl.conf

- 用户级调整
    - 用户能打开的文件描述符最大数量
        - 例子：vim /etc/security/limits.conf
            ```
            root     soft  nofile 1100000
            root     hard nofile 1100000
            *     soft  nofile 1100000
            *     hard nofile 1100000
            ```
