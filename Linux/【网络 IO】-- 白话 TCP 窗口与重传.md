### 概述

TCP 层主要提供 3 个功能：有序传输、超时重传、流量控制。下面的讨论涉及到的就是重传和流控。

---

### TCP 窗口

TCP 窗口之间的关系：**min(接收窗口，拥塞窗口) => 发送窗口**，即接受方的接收窗口和发送方的拥塞窗口之间的小者，决定着发送方的发送窗口大小。重传和流控也是可以围绕着 **“在当前的接收窗口大小和网络环境条件下，发送窗口应该多大”** 这个主题展开的。

#### 接收窗口

1. 直观认识接收窗口

接收窗口是几个窗口中最简单的。接收窗口指的是接收方自身的接收缓存大小，是在 TCP 3 次握手中告知对方的一个信息。下图演示的就是 192.168.1.102 和 59.37.96.63 在 3 次握手中分别交换的接收窗口大小信息：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/客户端接收窗口.png)

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/服务端接收窗口.png)


2. TCP Window Scale

在 TCP 刚被发明实现出来时，世界的网络带宽都很小，最大的接收窗口只有 65535B，也就差不多 65KB 大小。随着硬件的不断进步，65KB 早就成了性能瓶颈，由于 TCP 头留给接收窗口只有 16bit，所以最大也只能 2^16-1 个字节 (刚好就是65535B)。所以想在这个 TCP 头字段做文章是不可能了 (排除 IPv6)，幸好 TCP 头里面还有一个万能的 option 字段，因此在 option 字段中可以再通过 window scale 字段来扩展接收窗口的大小。如下图演示：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/WindowScale.png)

根据上图，192.168.1.102 的真实接收窗口大小应该是 65535 * 32 = 1706720B，大约 1.6MB。

摘抄自 wiki 上的一段关于 linux window scale 的描述：

```
Linux[edit]

This section contains instructions, advice, or how-to content. The purpose of Wikipedia is to present facts, not to train. Please help 
improve this article either by rewriting the how-to content or by moving it to Wikiversity, Wikibooks or Wikivoyage. (February 2016)
Linux kernels (from 2.6.8, August 2004) have enabled TCP Window Scaling by default. The configuration parameters are found in the /proc 
filesystem, see pseudo-file /proc/sys/net/ipv4/tcp_window_scaling and its companions /proc/sys/net/ipv4/tcp_rmem and 
/proc/sys/net/ipv4/tcp_wmem (more information: man tcp, section sysctl).[7]

Scaling can be turned off by issuing the command sysctl -w "net.ipv4.tcp_window_scaling=0" as root. To maintain the changes after a 
restart, include the line "net.ipv4.tcp_window_scaling=0" in /etc/sysctl.conf (or /etc/sysctl.d/99-sysctl.conf as of systemd 207).
```

可以得知 linux 下的 window scale 默认是开启的，并且可以通过 `/proc/sys/net/ipv4/tcp_window_scaling` 控制开启和关闭，1 代表开启，0 代表关闭。同时 `/proc/sys/net/ipv4/tcp_rmem` 和 `/proc/sys/net/ipv4/tcp_wmem` 的调优也是在 window scale 开启的状态下才有作用的。

3. 查看和调整接收窗口大小

```
# 查看接收窗口大小，三个数字分别是最小、默认、最大接收窗口大小
shell> cat /proc/sys/net/ipv4/tcp_rmem
4096	87380	6291456

# 调整接收窗口大小
shell> echo 1048576 1048576 1048576 > /proc/sys/net/ipv4/tcp_rmem
```

4. 接收窗口与发送窗口的关系

因为接收窗口和拥塞窗口共同决定着发送窗口，因此先做两个假设，来排除拥塞窗口的影响：1. 假设接收窗口非常小。原因是：这样拥塞窗口将很可能永远都不会触碰到拥塞点，接收窗口也成了影响发送窗口的最大因素了；2. 网络非常顺畅，拥塞窗口可以增长的大小远远大于接收窗口。

基于上面任意一个假设，当接收窗口减小时，发送窗口也会随着减小，这就是 TCP 的滑动窗口机制。

5. 一些实用建议

- 在网络环境很差的情况下，调小接收窗口可以提升性能
- 在网络环境良好的情况下，调大接收窗口可以提升性能
- 上面两点的前提和操作如果互换，将会产生反效果
- 在想要调大接收窗口的时候，要检查下系统是否支持并开启了 window scale

> 当网络环境很差时 (比如频繁发生网络线路的拥塞)，调大接收窗口反而会让发送方频频触碰拥塞点，从而触发发送方的超时重传，发送方大部分时间也将处于慢启动过程中，严重影响网络 IO 性能。

#### 拥塞窗口

拥塞窗口是由内核提供的拥塞控制算法维护的，可以通过 `/proc/sys/net/ipv4/tcp_congestion_control` 查看，演示如下：

```
shell> cat /proc/sys/net/ipv4# cat tcp_congestion_control 
cubic
```

1. 拥塞窗口的维护阶段

```
建立连接 -- 慢启动 -- 拥塞避免 -- 拥塞发生 -- 超时重传 -- 慢启动 -- 拥塞避免
                                         |
                                         -- 快速重传 -- 快速回复 -- 拥塞避免
```

*这个图需要说明下，其实拥塞发生也有可能发生在慢启动阶段，不一定是在拥塞避免阶段*

2. 慢启动

慢启动主要是初始化拥塞窗口的大小，并试逐渐增加拥塞窗口的大小。刚建立连接后，发送方对网络环境一无所知，如果一口气发太多数据可能会立刻触碰到拥塞点。RFC 建议拥塞窗口的初始大小为 2～4 个 MSS (每个 TCP 包能携带的最大数据量，一般是 MTU - 40B = 1460B，40 是 TCP 头和 IP 头的大小之和)。如果发出去的包都得到了确认，则表明没有触碰到拥塞点，可以继续增大拥塞窗口。

RFC 建议在慢启动阶段，没得到 n 个确认，就将拥塞窗口增加 n 个 MSS。

3. 拥塞避免

慢启动持续一段时间后，拥塞窗口就会增长得很大，也更容易触碰到拥塞点。此时，内核通过 sstresh 参数来控制拥塞窗口的增长，一旦拥塞窗口的大小超过 sstresh 就会进入拥塞避免阶段。相比慢启动，拥塞避免对于拥塞窗口增长的控制非常严格。

RFC 建议每得到一个确认，就增加 1 个 MSS。

sstresh 的值可以通过 `ss` 命令查看，演示如下：

```
shell> ss -i | grep ssthres
	 cubic wscale:5,7 rto:204 rtt:0.169/0.029 ato:40 mss:1448 cwnd:3 ssthresh:2 send 205.6Mbps retrans:0/79 rcv_rtt:4 rcv_space:28960
	 cubic wscale:5,7 rto:204 rtt:0.185/0.029 ato:64 mss:1448 cwnd:10 ssthresh:7 send 626.2Mbps retrans:0/13 rcv_rtt:4 rcv_space:28960
	 cubic wscale:5,7 rto:204 rtt:0.213/0.024 ato:40 mss:1448 cwnd:10 ssthresh:13 send 543.8Mbps rcv_rtt:4 rcv_space:28960
	 cubic wscale:5,7 rto:204 rtt:0.191/0.051 ato:40 mss:1448 cwnd:10 ssthresh:7 send 606.5Mbps rcv_rtt:4 rcv_space:28960
```

- `wscale`：window scale
- `rto`：超时等待时间
- `rtt`：往返时间
- `cwnd`：拥塞窗口大小
- `ssthresh`：拥塞避免临界值

4. 拥塞发生

拥塞避免阶段如履薄冰，因为网络环境一旦变差，发送发就会触碰到拥塞点，接着要么是触发超时重传，要么是触发快速重传。两者都会影响性能，只是后者更小。

5. 超时重传

终于到性能杀手超时重传了。当网络环境频繁拥塞，很可能就会发生丢包，一旦丢包，发送方就会等待 1 个 rto 时间，然后再重新发送没被确认的数据包，并且，拥塞窗口会急剧下降，发送方将再次进入慢启动阶段。

RFC 建议拥塞窗口调整为 max(拥塞时没被确定的数据量的 1/2，2*MSS)。

超时之所以对性能影响大，正式因为在 rto 时间内，是没有做任何事情的，干等着，同时，拥塞窗口还会大幅度的下降，最差是降到 2 个 MSS，又要重新走一遍慢启动。

通过抓包找到的疑似重传的数据包，演示如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/超时重传1.png)

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/超时重传2.png)

> 小文件更容易触发超时重传

6. 快速重传 & 快速回复

当接收方发现传丢了数据包后，通过连续向发送方发送 3 个。快速重传相比超时重传的性能消耗更小，因为快速重传无需等待 rto 时间，并且拥塞窗口的下降程度也更低。这种低幅度的拥塞窗口下降就叫快速回复。

RFC 建议拥塞窗口调整为 ssthres+3*MSS。

通过抓包直观看下快速重传，演示如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/快速重传.png)

那么为什么是 3 个 dup ack 呢？首先因为 TCP 数据包在接收方收到的时候有可能是乱序的，在乱序的时候，接收方也会发送一个 dup ack；同时，一般乱序包之间的不会相差太远，比如 3 号包可能会跑到 5 号包后面，但是不太可能跑到 9 号包后面。而因为乱序而进行重传是没必要的。所以，一般乱序的情况下，接收方在发出第一个 dup ack 包后，很快就会收到那个乱序包 (比如 3 号包)，比较难可以连续凑够 3 个 dup ack 包。

那么为什么快速重传就可以快速恢复，而不必像超时重传那样重新进入慢启动呢？因为既然发送方可以收到 3 个连续的 dup ack 包，证明网络环境还是可以的，之前的丢包算是短暂性的少量丢包，网络知识轻微的抖动而已，没必要使用等待 rto 和慢启动这些极大降低自身网络性能的手段来减轻网络环境的负担。

7. 一些实用建议

- 关于 rto：如果通过 `ss -i` 检查到 rto 的值太大 (默认 200ms)，比如 1s，不要犹豫立马改 => `ip route change default via 你的网关 dev 你的网卡设备号 rto_min 5ms`
- 关于拥塞点：如果频繁发生超时重传，可以根据 wireshark 提供的统计图计 -- io graphs，由 package/s 和 mss 计算出这些重传时刻的拥塞点是多少；然后通过将接受窗口的大小控制在这个拥塞点之下，从而让发送窗口可以避免触点，减少超时重传的发生。演示如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/拥塞点.png)






