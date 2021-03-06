![](https://raw.githubusercontent.com/hsxhr-10/picture/master/Block%20Device%20Layer.png)

---

### <font color=#00b0f0>物理结构</font>

#### 机械磁盘

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/%E6%9C%BA%E6%A2%B0%E7%A3%81%E7%9B%981.jpg)

核心部件：

- 磁头臂：负责寻道
- 磁头：负责读写
- 磁盘：负责存储数据
- 主轴：负责旋转磁盘

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/%E6%9C%BA%E6%A2%B0%E7%A3%81%E7%9B%982.jpg)

磁盘的结构：

- 磁道
- 扇面
- 扇区
- 族 (数据库优化相关的内容经常碰到的词汇)

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/%E6%9C%BA%E6%A2%B0%E7%A3%81%E7%9B%983.jpg)

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/%E6%9C%BA%E6%A2%B0%E7%A3%81%E7%9B%984.jpg)

一次磁盘的读/写的过程：

- 磁头臂/磁头寻道，即移动到目标数据所在的磁道上
- 主轴循转磁盘，直到磁头和目标数据所在的扇区相遇
- 磁头对扇区进行读/写

一些供参考的速度对比

- 机械磁盘比 SRAM (CPU 的三级缓存) 慢 40000 倍
- 机械磁盘比 DRAM (内存) 慢 2500 倍

#### 固态磁盘

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/%E5%9B%BA%E6%80%81%E7%A3%81%E7%9B%98.jpg)

固态磁盘由多个块组成，每个块中又包含多个页。当需要对某个页写入数据时，需要移动其他页，并擦出整个块，才能进行写入操作。同时固态磁盘会因为写操作减少寿命，但是读操作并不会。比如有一块固态磁盘，擦除限制是 3000 次，容量是 256GB，即理论上写入 750TB 的数据后该磁盘就会报废，这个也是理论上的值，也有可能在写入 750TB 后还能坚持一段时间。当然对于普通的个人用户来说，每天也就大概写入几 GB 的数据，假设 10GB，也要 210 年才能让磁盘报废。但是对于一些大型非实时的 I/O 密集型服务来说，在选择磁盘时就要深思熟虑了。

---

### <font color=#00b0f0>工作原理</font>

CPU 读取磁盘数据工作过程：

```
1、CPU 发送 I/O 请求到内核 I/O Scheduler
2、I/O Scheduler 负责调度请求队列，通过 I/O 总线将 I/O 请求发送到磁盘控制器
3、磁盘控制器完成寻道、磁盘旋转、读取操作，并将数据通过 I/O 总线、内存总线传输到内存
4、磁盘控制器通过中断的方式通知 CPU I/O 请求已经完成
5、CPU 通过系统总线、内存总线传输内存中的数据
```

如下图所示：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/%E7%A3%81%E7%9B%98%E5%B7%A5%E4%BD%9C%E5%8E%9F%E7%90%86.png)

---

### 机械 VS 固态

balabala...
