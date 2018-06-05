### 测试指标

- 延迟：即完成一个 CPU 周期所需的时间

---

### 工具

- cyclictest：负责测试延迟

---

### 测试示例

*注意：下面的测试机器都是单物理核，多逻辑核的云服务器*

#### 测试延迟

```
# 测试服务器 1 的 CPU 情况
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
# 测试服务器 2 的 CPU 情况
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


