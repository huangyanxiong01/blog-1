### 概述

TCP 层主要提供 3 个功能：有序传输、超时重传、流量控制。下面的讨论涉及到的就是重传和流控。

---

### TCP 窗口

TCP 窗口之间的关系：min(接收窗口，拥塞窗口) => 发送窗口，即接受方的接收窗口和发送方的拥塞窗口之间的小者，决定着发送方的发送窗口大小。重传和流控也是围绕着 **“在当前的接收窗口大小和网络环境条件下，发送窗口应该多大”** 这个主题的。

#### 接收窗口

1. 直观认识接收窗口

接收窗口是几个窗口中最简单的。接收窗口指的是接收方自身的接收缓存大小，是在 TCP 3 次握手中告知对方的一个信息。下图演示的就是 192.168.1.102 和 59.37.96.63 在 3 次握手中分别交换的接收窗口大小信息：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/客户端接收窗口.png)

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/服务端接收窗口.png)


2. TCP Window Scale

在 TCP 刚被发明实现出来时，世界的网络带宽都很小，最大的接收窗口只有 65535B，也就差不多 65KB 大小。随着硬件的不断进步，65KB 早就成了性能瓶颈，由于 TCP 头留给接收窗口只有 16bit，所以最大也只能 2^16-1 个字节 (刚好就是65535B)。所以想在这个 TCP 头字段做文章是不可能了 (排除 IPv6)，幸好 TCP 头里面还有一个万能的 option 字段，因此在 option 字段中可以再通过 window scale 字段来扩展接收窗口的大小。如下图演示：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/WindowScale.png)
