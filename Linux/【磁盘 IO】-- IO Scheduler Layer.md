![](https://raw.githubusercontent.com/hsxhr-10/picture/master/I%3AO%20Scheduler%20Layer.png)

---

### 概述

I/O Scheduler Layer 处于 Generic Block Layer 和 Block Device Driver 之间。它的主要功能有两个，1 是合并相邻的 I/O 请求，2 是对 I/O 请求进行调度 (重新排序也属于调度)。

