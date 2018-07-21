#### 1. 下面是经典的 TCP 头结构：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/TCP头.png)

字段的取值范围：

- src port：取值范围 [0, 2^16 - 1 = 65535]
- dest port：同上
- sequence number： 取值范围 [0, 2^32 - 1 = 4294967296 (42亿)]
- ack number：同上
- header size：该字段的单位是 32 bit 不是 1 bit。即 tcp header 的取值 [20 Byte, (2^4 - 1)*32 / 8 = 60 Byte]
- window size：意味着接收窗口在还没算上 window scale 之前取值范围 [0 Byte, 65535 Byte]

#### 2. 通过 wireshark 看 TCP 头

*对于 wireshark 额外添加的字段，只对有必要的进行说明。*

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/从wireshark看tcp头1.png)

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/从wireshark看tcp头2.png)

字段详解：

- Source Port：该 TCP 包的源端口
- Destination Port：该 TCP 包的目的端口
- [TCP Segment Len]：wireshark 的额外字段。TCP 数据包长度。下一次的 Sequence number = 当前 Sequence number + 当前 [TCP Segment Len]
- Sequence number：该 TCP 包的序列号
- [Next Sequence number]：wireshark 的额外字段。下一次 TCP 包的序列号
- Acknowledgment number：本端已经收到的最新 TCP 包的序列号
- Head Length：TCP 头大小，单位是 32 bit
- Flags
  - Congestion Window Reduced：wireshark 的额外字段。根据该标记可以判断是否发生网络拥塞，再进一步判断是超时重传还是快速重传
  - Urgent：对应 TCP 头中的 URG。标记该数据包应该被中间设备尽快传递
  - Acknowledgment：对应 TCP 头中的 ACK。标记该 TCP 包为应答包
  - Push：对应 TCP 头中的 PSH。标记该 TCP 包应该尽快交付给应用层
  - Rest：对应 TCP 头中的 RST。标记该 TCP 包是回应某种异常情况，[参考](https://github.com/hsxhr-10/blog/blob/master/Linux/【网络%20IO】--%20TCP%20头.md#4-rst-发送情景)
  - Syn：对应 TCP 头中的 SYN。标记该 TCP 包是跟三次握手相关
  - Fin：对应 TCP 头中的 FIN。标记该 TCP 包是跟四次挥手相关
- Window size value：本端接收窗口大小，还没算上 window scale 的 window size
- [calculated window size]：wireshark 的额外字段。算上 window scale 之后的 window size
- Checksum：验证数据包在传输过程中没有损坏
- Urgent pointer：TODO

#### 3. ACK 种类

- 延迟 ACK：接收方会在一个 ACK 时间窗口内等待尽可能多的数据包，如果在 ACK 时间窗口内内又收到几个数据包，那么将会一次性地应答；如果在 ACK 时间窗口内没有接收到数据包，那么会在窗口结束后应答
- 连带 ACK：接收方在应答时间窗口内刚好要给发送方发数据包，那么应答将会随着要发送的数据包一块发送过去

> 延迟发送和连带发送的目的都是为了减少数据包的发送，提高效率

- winsize ACK：更新接收窗口大小
- 乱序 ACK：数据包乱序会导致接收方回发一个 ACK 包

- 快速重传 ACK：触发快速重传时会连续回发 3 个 ACK 包，乱序和快速重传的区别参考 [这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【网络%20IO】--%20白话%20TCP%20窗口与重传.md#拥塞窗口)

#### 4. RST 种类

- 向已经建立好的连接再次发出 SYN 包
- 像一个已经关闭的连接读写数据

> TCP 连接无论在什么情况下只要收到 RST 包，都会进入 CLOSED 状态






