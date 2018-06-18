### TCP 三次握手

灵魂画手上线！

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/三次握手.jpeg)

1. 过程及状态

- CLOSED：为了方便描述初始状态的一个假想状态
- LISTEN：服务端调用 socket api 中的 `socket`, `bind`, `listen`，并进入监听请求状态
- SYN_SENT：客户端调用 socket api 中的 `socket`, `connect`发出 SYN 包，并进入 SYN_SENT 状态等服务端回应
- SYN_RCVD：服务端接收到客户端的 SYN 包，从 LISTEN 进入 SYN_RCVD 状态，并向客户端发送 ACK 包和 SYN 包
- 客户端 ESTABLISHED：客户端接收到服务端的 ACK 包和 SYN 包，从 SYN_SENT 进入 ESTABLISHED 状态，并向服务端发送 ACK 包
- 服务端 ESTABLISHED：服务端接收到客户端的 ACK 包，从 SYN_RCVD 进入 ESTABLISHED 状态

至此，连接就建立起来了，可以进行数据交换了。

2. 
