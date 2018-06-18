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

问题 1：通过 `netstat antp` 命令发现服务器存在大量 SYN_RECV 状态的 TCP 连接。

- (1) 大量客户端有没有收到服务端的 [SYN, ACK] 响应，从而使服务端停留在 SYN_RECV 状态不断重发
  - 解决：通过从服务端 ping 客户端来确定是否网络不通
- (2) 客户端收到了响应
  - (2.1) 客户端虽然收到了，但是压根没想过要回 ACK (这就是 SYN Flood 攻击了)
    - 解决 1：通过 iptables 控制
      ```
      iptables -A INPUT -p tcp --syn -m limit --limit 500/s -j ACCEPT
      ```
    - 解决 2：通过内核 TCP SYNC 参数
      ```
      echo 1 > /proc/sys/net/ipv4/tcp_syncookies  # 开启 syncookies 协助抵御 SYN Flood
      echo 2048 > /proc/sys/net/ipv4/tcp_max_syn_backlog  # 增大 sync 队列长度
      echo 3 > /proc/sys/net/ipv4/tcp_synack_retries  # 减少服务端 [SYNC, ACK] 重传次数
      ```
  - (2.2) 客户端收到了有问题的 [SYN, ACK]
    - 解决：通过抓包工具分析客户端的 SYN 包中的目的 ip 是否等于服务端 [SYN, ACK] 包中的源 ip。看是否在响应过程中 [SYNC, ACK] 包的源 ip 地址被错误修改成了负载均衡器、防火墙等设备的地址

---

### TCP 四次挥手

持续高能！ (*下面说的发送方指的是主动关闭方，接收方指的是被动关闭方*)

四次挥手有三种情况。

第一种情况是比较理想的，接收方在收到发送方的 FIN 包之后才回应 FIN 包。

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/四次挥手1.png)

> 这种情况下发送方的状态变化是 ESTABLISHED => FIN_WAIT1 => FIN_WAIT2 => TIME_WAIT => CLOSED

第二种情况则是发送方的 FIN 包在传输的途中时 (即接收方还没收到这个 FIN 包)，接收方也发出了 FIN 包，既可以认为发送方和接收方同时发出 FIN 包，并且发送方先收到接收方的 FIN 包，再收到响应的 ACK 包。

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/四次挥手2.png)

> 这种情况下发送方的状态变化是 ESTABLISHED => FIN_WAIT1 => CLOSING => TIME_WAIT => CLOSED

1. 状态及过程

第一种情况：

- FIN_WAIT1：发送方调用 socket api 中的 `close`，向接收方发送 FIN 包，状态从 ESTABLISHED 进入 FIN_WAIT1
- CLOSE_WAIT：接收方接收到 FIN 包，并回应 ACK 包，状态从 ESTABLISHED 进入 CLOSE_WAIT (处于该状态往往是因为还有数据交换操作没完成，或者是等待上层应用调用 `close`)
- FIN_WAIT2：发送方接收到 ACK 包，状态从 FIN_WAIT1 进入 FIN_WAIT2
- LAST_ACK：接收方调用 `close` 发送 FIN 包，状态从 CLOSE_WAIT 进入 LAST_ACK
- TIME_WAIT：发送方接收到 FIN 包，状态从 FIN_WAIT2 进入 TIME_WAIT，并回应 ACK 包
- 接收方 CLOSED：接收方接收 ACK 包，状态从 LAST_ACK 进入 CLOSED
- 发送方 CLOSED：发送方等待 2 个 MSL 时间后，状态从 TIME_WAIT 进入 CLOSED

第二种情况：

- FIN_WAIT1：发送方调用 socket api 中的 `close` 向接收方发送 FIN 包，状态从 ESTABLISHED 进入 FIN_WAIT1
- (close)：在 FIN 包还在网络上传输的时候，接收方调用了 `close` 向发送方发送 FIN 包
- CLOSING：发送方接收到 FIN 包，状态从 FIN_WAIT1 进入 CLOSING
- LAST_ACK：接收方接收到 FIN 包，进入 LAST_ACK 状态，并回应 ACK 包
- TIME_WAIT：发送发接收到 ACK 包，状体从 CLOSING 进入 TIME_WAIT，并回应 ACK 包
- 接收方 CLOSED：接收方接收到 ACK 包，状态从 LAST_ACK 进入 CLOSED
- 发送方 CLOSED：发送方等待 2 个 MSL 时间后，状态从 TIME_WAIT 进入 CLOSED

> 两种情况的主要区别是接收方是否在还没有收到 FIN 包之前就发起了关闭请求。

2. 从 wireshark 看四次挥手

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/从wireshark看四次挥手.png)

上面是四次挥手中的第一种情况。在实际的情况中，19 号数据包是可以发出 [FIN, ACK] 这样的数据包的，那是不是意味着其实 18 号的数据包是没必要要的，四次挥手可以变成三次挥手？其实不然，因为 220.181.57.216 在接收到 17 号包之后是可以等一段时间再选择发出 FIN 包的 (也就是 CLOSE_WAIT 到 LAST_ACK 之间的时间)，但是 ACK 包却是必须要赶紧回应的，所以 18 号包并不是多余的，正式因为 18 号包的存在，才使得 CLOSE_WAIT 到 LAST_ACK 之间的时间能够存在。

3. TIME_WAIT 和 MSL

MSL 指的是 TCP 数据段能在网络上存在的最长时间。

```
# 查看 2*MSL，即 TIME_WAIT 的等待时间，默认 60s
shell> cat /proc/sys/net/ipv4/tcp_fin_timeout
60

# 修改 2*MSL
SHELL> echo 5 > /proc/sys/net/ipv4/tcp_fin_timeout
```

TIME_WAIT 状态下等待 2 个 MSL 的原因：

- 如果发送方在发送完最后一个 ACK 包之后立刻关闭，且 ACK 包在传输过程中丢包了，那么接收方将会发起重传，但是发送方已经关闭了，因此会导致接收方无法正确关闭连接。TCP 是全双工通信，关闭时也需要确保双方都能顺利关闭连接
- 假设双方因为某些原因非正常关闭了连接，但是立刻又建立起了新的连接，且 tcp/ip 四元组和刚刚关闭的连接相同，那么新建立起的连接可能会接收到旧连接的残余数据。因此需要等上 2 个 MSL 时间，确保残余数据完全消失，不会影响新的连接

4. 相关问题及解决

(PS：对于发送方来说)

问题 1：通过 `netstat -antp` 发现有大量 FIN_WAIT1 状态的 TCP 连接。

- 





