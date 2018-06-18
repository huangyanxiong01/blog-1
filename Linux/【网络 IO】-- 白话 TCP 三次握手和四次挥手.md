### TCP 三次握手

灵魂画手上线！

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/三次握手.jpeg)

1. 状态及过程

- CLOSED：为了方便描述初始状态的一个假想状态
- LISTEN：服务端调用 socket api 中的 `socket`, `bind`, `listen`，并进入监听请求状态
- SYN_SENT：客户端调用 socket api 中的 `socket`, `connect`发出 SYN 包，并进入 SYN_SENT 状态等服务端回应
- SYN_RCVD：服务端接收到客户端的 SYN 包，从 LISTEN 进入 SYN_RCVD 状态，并向客户端发送 ACK 包和 SYN 包
- 客户端 ESTABLISHED：客户端接收到服务端的 ACK 包和 SYN 包，从 SYN_SENT 进入 ESTABLISHED 状态，并向服务端发送 ACK 包
- 服务端 ESTABLISHED：服务端接收到客户端的 ACK 包，从 SYN_RCVD 进入 ESTABLISHED 状态

至此，连接就建立起来了，下面就可以进行数据交换了。需要注意的是，客户端在 SYN_SENT 状态下如果发现服务端是不可连接的，将会直接进入 CLOSED 状态。

2. 从 wireshark 看三次握手

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/从wireshark看三次握手.png)

6~8 号数据包就是一次 TCP 三次握手，192.168.1.101 是客户端，220.181.57.216 是服务端。在握手的过程中，客户端和服务端除了建立连接外，还彼此交换了很多必要的信息，比如接收窗口有多大 (`Win` 字段)，是否有开启 window scale (`WS` 字段)，MSS 是多大。关于 window size 的大小计算可以参考 [这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【网络%20IO】--%20白话%20TCP%20窗口与重传.md#接收窗口)。

3. 相关问题及解决

问题1：通过 `netstat antp` 命令发现服务器存在大量 SYN_RECV 状态的 TCP 连接。

- 第一种情况是大量的客户端有没有收到服务端的 [SYN, ACK] 响应从而进行重发了
  - 解决：通过从服务端 ping 客户端来确定
- 第二种情况是客户端收到了响应
  - 客户端虽然收到了，但是没想过要回 ACK。这就是 SYN Flood 攻击了
    - 解决1：通过 iptables 控制 `iptables -A INPUT -p tcp --syn -m limit --limit 500/s -j ACCEPT`
    - 解决2：修改内核 TCP 参数
      ```
      echo 1 > /proc/sys/net/ipv4/tcp_syncookies
      echo 2048 > /proc/sys/net/ipv4/tcp_max_syn_backlog
      echo 3 > /proc/sys/net/ipv4/tcp_synack_retries
      ```
  - 客户端收到了有问题的 [SYN, ACK]。分析客户端的 SYN 包中的目的 ip 是否等于服务端 [SYN, ACK] 包中的源 ip，肯是否在转发的过程中 ip 地址被负载均衡器、防火墙等设备错误修改了


