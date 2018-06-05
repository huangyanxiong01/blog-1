### 测试指标

- 延迟：即完成一个 CPU 周期所需的时间

---

### 工具

- cyclictest：负责测试延迟

---

### 测试示例

*注意：下面的测试机器的多核指的是逻辑核，且都是云服务器*

#### 测试延迟

```
# 服务器 1 的 CPU 情况
root@iZbp107984k6l9khwapbruZ:~# lscpu 
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                4
On-line CPU(s) list:   0-3
Thread(s) per core:    1
Core(s) per socket:    4
Socket(s):             1
NUMA node(s):          1
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 79
Stepping:              1
CPU MHz:               2494.220
BogoMIPS:              4988.44
Hypervisor vendor:     KVM
Virtualization type:   full
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              40960K
NUMA node0 CPU(s):     0-3

# 测试结果
root@iZbp107984k6l9khwapbruZ:~# cyclictest -D 300s q
# /dev/cpu_dma_latency set to 0us
WARN: Running on unknown kernel version...YMMV
policy: other/other: loadavg: 0.00 0.04 0.69 1/235 9864          

T: 0 ( 9136) P: 0 I:1000 C: 299848 Min:      5 Act:   11 Avg:   11 Max:   21205
```

```
# 服务器 2 的 CPU 情况
root@iZ231l9tsglZ:~# lscpu 
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                2
On-line CPU(s) list:   0,1
Thread(s) per core:    2
Core(s) per socket:    1
Socket(s):             1
NUMA node(s):          1
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 62
Stepping:              4
CPU MHz:               2593.748
BogoMIPS:              5187.49
Hypervisor vendor:     KVM
Virtualization type:   full
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              20480K
NUMA node0 CPU(s):     0,1

# 测试结果
root@iZ231l9tsglZ:~# cyclictest -D 300s q
# /dev/cpu_dma_latency set to 0us
policy: other/other: loadavg: 1.17 0.99 0.91 1/513 30696           

T: 0 (21462) P: 0 I:1000 C: 296034 Min:     10 Act:   27 Avg:   55 Max:   19410
```

```
# 服务器 3 的 CPU 情况
root@iZwz960qbyq1j1qda2lvdoZ:~# lscpu 
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                1
On-line CPU(s) list:   0
Thread(s) per core:    1
Core(s) per socket:    1
Socket(s):             1
NUMA node(s):          1
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 85
Stepping:              4
CPU MHz:               2500.000
BogoMIPS:              5000.00
Hypervisor vendor:     KVM
Virtualization type:   full
L1d cache:             32K
L1i cache:             32K
L2 cache:              1024K
L3 cache:              33792K
NUMA node0 CPU(s):     0

# 测试结果
root@iZwz960qbyq1j1qda2lvdoZ:~# cyclictest -D 300s q
# /dev/cpu_dma_latency set to 0us
policy: other/other: loadavg: 0.22 0.08 0.04 1/224 22971          

T: 0 (22963) P: 0 I:1000 C: 299906 Min:      6 Act:   11 Avg:   18 Max:    4835
```

```
# 服务器 4 的 CPU 情况
root@iZbp175df13v7q2t1t1ddgZ:~# lscpu 
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                1
On-line CPU(s) list:   0
Thread(s) per core:    1
Core(s) per socket:    1
Socket(s):             1
NUMA node(s):          1
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 45
Stepping:              7
CPU MHz:               2300.022
BogoMIPS:              4600.04
Hypervisor vendor:     Xen
Virtualization type:   full
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              15360K
NUMA node0 CPU(s):     0

# 测试结果
root@iZbp175df13v7q2t1t1ddgZ:~# cyclictest -D 300s q
# /dev/cpu_dma_latency set to 0us
policy: other/other: loadavg: 1.09 1.15 1.03 2/252 6806            

T: 0 (32363) P: 0 I:1000 C: 298471 Min:     12 Act:   30 Avg:   41 Max:    7497
```

我们主要关注 `Avg` 字段的值，越小代表 CPU 的延迟越小。

对于服务器的 CPU 重点看几个参数 `CPU(s)`, `CPU MHz`, `L1d cache`, `L1i cache`, `L2 cache`, `L3 cache`，可以看到 4 个测试服务器的 `CPU MHz` 字段基本相同，重点分析其他参数对 CPU 延迟的影响。

- 对于服务器 1 和 2/3/4 来说，当 CPU 核数和三级缓存之和都存在差距时，服务器 1 的 `Avg` 值明显小于其他三台服务器。
- 对于服务器 1 和 3 来说，CPU 核数差距较大，差了 4 倍，但是 1 和 3 的 `L1d cache`, `L1i cache` 相同，3 的 `L2 cache` 是 1 的 4 倍，3 的 `L3 cache` 比 1 少几百 KB。结果 3 的 `Avg` 和 1 的 `Avg` 并没有相差很大，说明除了核数，三级缓存对 CPU 的延迟影响也很大。
- 对于服务器 3 和 2/4，虽然 3 的核数 <= 2/4，但是三级缓存之和却平均多了 16500KB，更重要的是二级缓存是它们的 4 倍，所以 3 的 `Avg` 值比 2/4 少了 4-5 倍。
- 对于服务器 2 和 4 来说，虽然 2 的核数是 4 的 2 倍，三级缓存之和多了五千多 KB，但是 2 的 `Avg` 值却比 4 要高，这咋一看不合理，但是由于这些都是通过虚拟化技术虚拟出来的云服务器，并且 2 和 4 是在不同的区域，同时 2 是一个人满为患的老区，4 是人相对少的新区，这也可以说明老区的云服务器对物理资源的争夺比新区要激烈，老区的物理资源也没有新区的充裕。
