### 测试指标

- 延迟：即完成一个 CPU 周期所需的时间

---

### 工具

- cyclictest：负责测试延迟

---

### 测试示例

*注意：下面的测试机器的多核指的是逻辑核*

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

对于服务器的 CPU 重点看几个参数 `CPU(s)`, `CPU MHz`, `L1d cache`, `L1i cache`, `L2 cache`, `L3 cache`，可以看到 4 个测试服务器的 `CPU MHz` 字段基本相同，重点分析其他参数对 CPU 延迟的影响。

当 CPU 核和三级缓存
