### TCP 三次握手

灵魂画手上线！

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/三次握手.jpeg)

1. 状态详解

- CLOSED：为了方便描述初始状态的一个假想状态
- LISTEN：服务端监听请求。对应 socket api 中的 `socket`, `bind`, `listen`
- SYN_SENT：客户端发出 SYN 包，并等服务端回应。对应 socket api 中的 `socket`, `connect`
- SYN_RCVD：服务端接收到客户端的 SYN 包，并向客户端发送 ACK 包和 SYN 包
- ESTABLISHED：
