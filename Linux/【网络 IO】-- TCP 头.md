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

- Source Port：对应 TCP 头中的 16 位源端口
- Destination Port：对应 TCP 头中的 16 目的端口
- [TCP Segment Len]：wireshark 的额外字段。TCP 数据包长度。下一次的 Sequence number = 当前 Sequence number + 当前 [TCP Segment Len]
- Sequence number：对应 TCP 头中的 32 序列号
- [Next Sequence number]：wireshark 的额外字段。下一次的 TCP 数据包序列号
- Acknowledgment number：对应 TCP 头中的 32 确认号。下一次的 Acknowledgment number = 当前 Acknowledgment number + 下一次接收到的 [TCP Segment Len]
- Head Length：TCP 头大小
- Flags
  - Congestion Window Reduced：wireshark 的额外字段。根据该标记可以判断是否发生网络拥塞，再进一步判断是超时重传还是快速重传
  - Urgent：对应 TCP 头中的 URG。表示 16 位紧急指针有效。用于催促中间设备要尽快传递该数据包
  - Acknowledgment：对应 TCP 头中的 ACK。用于标记 32 位确认号有效
  - Push：对应 TCP 头中的 PSH。用于接受方应该尽快将数据包交给应用层，尽量别再缓存中排队等待
  - Rest：对应 TCP 头中的 RST。用于异常关闭连接
  - Syn：对应 TCP 头中的 SYN。用于三次握手
  - Fin：对应 TCP 头中的 FIN。用于四次挥手
- Window size value：对应 TCP 头中的 16 位窗口大小。还没算上 window scale 的 window size
- [calculated window size]：wireshark 的额外字段。算上 window scale 之后的 window size
- Checksum：对应 TCP 头中的 16 位校验和。用于确保数据在传输过程中没有损坏
- Urgent pointer：对应 TCP 头中的 16 位紧急指针

#### 3. ACK 发送情景

正常情况：

- 收到一个数据包，启动定时器 (200ms)，定时器到点了，后一个数据包还没到，给前一个数据包回发 ACK 包。这叫延迟发送
- 收到一个数据包，启动定时器，定时器到点之前，又收到了至少一个数据包，给这几个数据包回发一个 ACK 包
- 收到一个数据包，启动定时器，定时器到点之前，要发点数据给发送方，钱一个数据包的 ACK 包就跟着想要发送的数据一块发过去了，这叫肖带发送
- 更新接收窗口大小
- 乱序导致立刻回发一个 ACK 包

快速重传：

- 触发快速重传时会连续回发 3 个 ACK 包，乱序和快速重传的区别参考 [这里](https://github.com/hsxhr-10/blog/blob/master/Linux/【网络%20IO】--%20白话%20TCP%20窗口与重传.md#拥塞窗口)

#### 4. RST 发送情景

- 连接一个没被监听的端口号
- 向已经建立好的连接再次发出 SYN 包
- 像一个已经关闭的连接读写数据
- socket api `close` 调用中指定 SO_LINGER 参数
- 服务器 A 要重启，收到 B 的 KEEP-ALIVED，A 会向 B 发送 RST 包

> TCP 连接无论在什么情况下只要收到 RST 包，都会进入 CLOSED 状态






