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
- [TCP Segment Len]：TCP 数据包长度。下一次的 Sequence number = 当前 Sequence number + 当前 [TCP Segment Len]
- Sequence number：当前的 TCP 数据包序列号
- [Next Sequence number]：下一次的 TCP 数据包序列号
- Acknowledgment number：TCP 数据包应答号。下一次的 Acknowledgment number = 当前 Acknowledgment number + 下一次接收到的 [TCP Segment Len]
- Head Length：TCP 头大小
- 
