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

6~8 号数据包就是一个三次握手的过程，192.168.1.101 是客户端，220.181.57.216 是服务端。在握手的过程中，客户端和服务端还相互交换了彼此的信息，比接收窗口有多大 (`Win` 字段)，是否有开启 window scale (`WS` 字段)，MSS 是多大。关于 window size 的大小计算可以参考 [这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【网络%20IO】--%20白话%20TCP%20窗口与重传.md#接收窗口)。

3. 
