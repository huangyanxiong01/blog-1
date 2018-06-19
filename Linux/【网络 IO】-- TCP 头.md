1. 下面是经典的 TCP 头结构：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/TCP头.png)

需要注意的一些数字：

- 16 位源端口号：意味着源端口的总个数是 2^16=65536，因为端口号从 0 开始算起，所以源端口的可用范围为 0~65535
- 16 位目的端口号：同上
- 32 位序列号：意味着序列号的总个数是 2^32=4294967296 (42亿)
- 32 位确认号：同上
- TCP 头大小：(16+16+32+32+4+6+6+16+16+16)bit / 8 = 20B

2. 通过 wireshark 看 TCP 头

*对于 wireshark 额外添加的字段，只对有必要的进行说明。*

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/从wireshark看tcp头1.png)

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/从wireshark看tcp头2.png)

字段详解：

- Source Port：源端口号
- Destination Port：目的端口号
- [TCP Segment Len]：TCP 数据包长度。下一次的 Sequence number = 当前 Sequence number + 当前 [TCP Segment Len]。wireshark 的额外字段
- Sequence number：当前的 TCP 数据包序列号
- [Next Sequence number]：下一次的 TCP 数据包序列号。wireshark 的额外字段
- Acknowledgment number：TCP 数据包应答号。下一次的 Acknowledgment number = 当前 Acknowledgment number + 下一次接收到的 [TCP Segment Len]
- Head Length：TCP 头大小
- Flags
  - Congestion Window Reduced：根据该标记可以判断是否发生网络拥塞，再进一步判断是超时重传还是快速重传。wireshark 的额外字段
  - Urgent：对应 TCP 头中的 URG。表示 16 位紧急指针有效。用于催促中间设备要尽快传递该数据包
  - Acknowledgment：对应 TCP 头中的 ACK。表示 32 位确认号有效
  - Push：对应 TCP 头中的 PSH。表示接受方应该尽快将数据包交给应用层，尽量别再缓存中排队等待
  - Rest：对应 TCP 头中的 RST。
  - Syn：对应 TCP 头中的 SYN。表示发起三次握手
  - Fin：对应 TCP 头中的 FIN。表示发起四次挥手
