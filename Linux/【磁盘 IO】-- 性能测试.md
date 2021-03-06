![](https://raw.githubusercontent.com/hsxhr-10/picture/master/Block%20Device%20Layer.png)

---

> 注意：本文所指的性能指标是磁盘硬件设备本身，不包括虚拟文件系统、真实文件系统、页缓存、通用块层、I/O Scheduler 层等内核部分，指的是裸盘

### <font color=#00b0f0>性能指标</font>

衡量磁盘的性能指标主要有三个：IOPS, Throughput, Latency

- **IOPS**
  - 随机读写 IOPS：指每秒能执行的随机读写次数，对应的场景是小文件的读写
  - 顺序读写 IOPS：指每秒能执行的顺序读写次数，对应的场景是大文件的读写
- **Throughput**：指单位时间内能成功传输的数据量，一般来说，该指标跟顺序读写 IOPS 的大小正相关
- **Latency**：指完成一次 I/O 需要花费的时间

一般来说，对于实时响应要求高的服务来说 (比如高性能数据库)，首选 SSD 磁盘来满足高 IOPS 和低 Latency 是最佳选择；而对于大吞吐量，对响应延迟不敏感的服务来说 (比如 Hadoop 离线计算)，选择 HDD 磁盘会更加合理。

---

### 待测指标

- 随机读 IOPS
- 随机写 IOPS
- 顺序读 IOPS
- 顺序写 IOPS
- 延迟

> IOPS 的值越大，延迟的值越小，磁盘性能越好

---

### 工具

- fio：用于测试 IOPS 相关
- ioping：用于测试延迟

> 注意：fio 测试会破坏文件系统，谨慎使用

---

### <font color=#00b0f0>运行环境</font>

```
# uname -a
Linux ubuntu 3.16.0-30-generic #40~14.04.1-Ubuntu SMP Thu Jan 15 17:43:14 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux

# cat /etc/*-release
DISTRIB_DESCRIPTION="Ubuntu 14.04.2 LTS"
```

---

### 测试示例

#### 测试随机写 IOPS

```
root@Lab:/home/tiger# fio -direct=1 -iodepth=128 -rw=randwrite -ioengine=libaio -bs=4k -size=1G -numjobs=1 -runtime=1000 -group_reporting -filename=/dev/dm-0 -name=Rand_Write_Testing

# 结果
Rand_Write_Testing: (g=0): rw=randwrite, bs=4K-4K/4K-4K/4K-4K, ioengine=libaio, iodepth=128
fio-2.1.3
Starting 1 process
Jobs: 1 (f=1): [w] [100.0% done] [0KB/53072KB/0KB /s] [0/13.3K/0 iops] [eta 00m:00s]
Rand_Write_Testing: (groupid=0, jobs=1): err= 0: pid=2749: Mon Jun  4 15:49:52 2018
  write: io=1024.0MB, bw=48273KB/s, iops=12068, runt= 21722msec
    slat (usec): min=1, max=10844, avg=19.38, stdev=55.05
    clat (usec): min=441, max=902146, avg=10580.11, stdev=22526.92
     lat (usec): min=520, max=902150, avg=10599.93, stdev=22526.97
    clat percentiles (usec):
     |  1.00th=[ 1752],  5.00th=[ 2832], 10.00th=[ 3696], 20.00th=[ 5152],
     | 30.00th=[ 6560], 40.00th=[ 7904], 50.00th=[ 9280], 60.00th=[10560],
     | 70.00th=[11968], 80.00th=[13504], 90.00th=[15552], 95.00th=[17280],
     | 99.00th=[31616], 99.50th=[45824], 99.90th=[230400], 99.95th=[407552],
     | 99.99th=[880640]
    bw (KB  /s): min=15074, max=56816, per=100.00%, avg=49291.00, stdev=9568.90
    lat (usec) : 500=0.01%, 750=0.01%, 1000=0.04%
    lat (msec) : 2=1.67%, 4=10.25%, 10=43.58%, 20=41.91%, 50=2.12%
    lat (msec) : 100=0.14%, 250=0.19%, 500=0.05%, 1000=0.05%
  cpu          : usr=11.56%, sys=40.50%, ctx=94661, majf=0, minf=8
  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%
     issued    : total=r=0/w=262144/d=0, short=r=0/w=0/d=0

Run status group 0 (all jobs):
  WRITE: io=1024.0MB, aggrb=48272KB/s, minb=48272KB/s, maxb=48272KB/s, mint=21722msec, maxt=21722msec

Disk stats (read/write):
    dm-0: ios=93/257932, merge=0/0, ticks=16/2715548, in_queue=2719824, util=99.85%, aggrios=180/257024, aggrmerge=0/5138, aggrticks=24/2705740, aggrin_queue=2708112, aggrutil=99.67%
  sda: ios=180/257024, merge=0/5138, ticks=24/2705740, in_queue=2708112, util=99.67%
```

重点看到 `write: io=1024.0MB, bw=48273KB/s, iops=12068, runt= 21722msec`，io=1024.0MB 代表随机写了 1GB 的数据；bw=48273KB/s 代表随机写速率为 47MB/s；iops=12068 代表随机写 IOPS 为 12068；runt= 21722msec 代表用时 21ms。

#### 测试随机读 IOPS

```
root@Lab:/home/tiger# fio -direct=1 -iodepth=128 -rw=randread -ioengine=libaio -bs=4k -size=1G -numjobs=1 -runtime=1000 -group_reporting -filename=/dev/dm-0 -name=Rand_Read_Testing 

# 结果
Rand_Read_Testing: (g=0): rw=randread, bs=4K-4K/4K-4K/4K-4K, ioengine=libaio, iodepth=128
fio-2.1.3
Starting 1 process
Jobs: 1 (f=0): [r] [100.0% done] [113.3MB/0KB/0KB /s] [28.1K/0/0 iops] [eta 00m:00s]
Rand_Read_Testing: (groupid=0, jobs=1): err= 0: pid=2759: Mon Jun  4 15:58:21 2018
  read : io=1024.0MB, bw=117133KB/s, iops=29283, runt=  8952msec
    slat (usec): min=1, max=43409, avg=15.49, stdev=125.99
    clat (usec): min=93, max=131649, avg=4351.59, stdev=3443.27
     lat (usec): min=97, max=131652, avg=4367.55, stdev=3447.78
    clat percentiles (usec):
     |  1.00th=[  948],  5.00th=[ 1432], 10.00th=[ 1800], 20.00th=[ 2416],
     | 30.00th=[ 2960], 40.00th=[ 3504], 50.00th=[ 3984], 60.00th=[ 4448],
     | 70.00th=[ 4832], 80.00th=[ 5472], 90.00th=[ 6560], 95.00th=[ 8256],
     | 99.00th=[15552], 99.50th=[19584], 99.90th=[50944], 99.95th=[63232],
     | 99.99th=[97792]
    bw (KB  /s): min=64552, max=148632, per=99.93%, avg=117051.71, stdev=26530.59
    lat (usec) : 100=0.01%, 250=0.01%, 500=0.04%, 750=0.16%, 1000=1.14%
    lat (msec) : 2=12.04%, 4=37.02%, 10=46.62%, 20=2.50%, 50=0.36%
    lat (msec) : 100=0.10%, 250=0.01%
  cpu          : usr=14.34%, sys=59.28%, ctx=11830, majf=0, minf=135
  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%
     issued    : total=r=262144/w=0/d=0, short=r=0/w=0/d=0

Run status group 0 (all jobs):
   READ: io=1024.0MB, aggrb=117133KB/s, minb=117133KB/s, maxb=117133KB/s, mint=8952msec, maxt=8952msec

Disk stats (read/write):
  sda: ios=251696/0, merge=2582/0, ticks=828892/0, in_queue=829596, util=98.86%
```

重点看到 `read : io=1024.0MB, bw=117133KB/s, iops=29283, runt=  8952msec`，io=1024.0MB 代表随机读了 1GB 数据；bw=117133KB/s 代表随机读的速率为 114MB/s；iops=29283 代表随机读 IOPS 为 29283； runt=  8952msec 代表用时 9ms。

#### 测试顺序写 IOPS

```
root@Lab:/home/tiger# fio -direct=1 -iodepth=64 -rw=write -ioengine=libaio -bs=1024k -size=1G -numjobs=1 -runtime=1000 -group_reporting -filename=/dev/dm-0 -name=Write_PPS_Testing

# 结果
Write_PPS_Testing: (g=0): rw=write, bs=1M-1M/1M-1M/1M-1M, ioengine=libaio, iodepth=64
fio-2.1.3
Starting 1 process
Jobs: 1 (f=1): [W] [100.0% done] [0KB/149.6MB/0KB /s] [0/149/0 iops] [eta 00m:00s]
Write_PPS_Testing: (groupid=0, jobs=1): err= 0: pid=2769: Mon Jun  4 16:04:08 2018
  write: io=1024.0MB, bw=240224KB/s, iops=234, runt=  4365msec
    slat (usec): min=61, max=5492, avg=288.99, stdev=305.86
    clat (msec): min=12, max=764, avg=271.19, stdev=183.88
     lat (msec): min=13, max=764, avg=271.49, stdev=183.86
    clat percentiles (msec):
     |  1.00th=[   18],  5.00th=[   24], 10.00th=[   31], 20.00th=[   64],
     | 30.00th=[   86], 40.00th=[  141], 50.00th=[  367], 60.00th=[  388],
     | 70.00th=[  408], 80.00th=[  429], 90.00th=[  449], 95.00th=[  494],
     | 99.00th=[  652], 99.50th=[  766], 99.90th=[  766], 99.95th=[  766],
     | 99.99th=[  766]
    bw (KB  /s): min=85088, max=834145, per=97.60%, avg=234458.38, stdev=244305.84
    lat (msec) : 20=2.73%, 50=11.82%, 100=24.02%, 250=3.32%, 500=54.30%
    lat (msec) : 750=3.22%, 1000=0.59%
  cpu          : usr=2.36%, sys=5.91%, ctx=206, majf=0, minf=10
  IO depths    : 1=0.1%, 2=0.2%, 4=0.4%, 8=0.8%, 16=1.6%, 32=3.1%, >=64=93.8%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=99.9%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued    : total=r=0/w=1024/d=0, short=r=0/w=0/d=0

Run status group 0 (all jobs):
  WRITE: io=1024.0MB, aggrb=240223KB/s, minb=240223KB/s, maxb=240223KB/s, mint=4365msec, maxt=4365msec

Disk stats (read/write):
    dm-0: ios=0/2302, merge=0/0, ticks=0/497620, in_queue=515700, util=97.22%, aggrios=86/2048, aggrmerge=0/254, aggrticks=8/526084, aggrin_queue=526072, aggrutil=96.83%
  sda: ios=86/2048, merge=0/254, ticks=8/526084, in_queue=526072, util=96.83%
```

重点看到 `write: io=1024.0MB, bw=240224KB/s, iops=234, runt=  4365msec`，io=1024.0MB 代表顺序写了 1GB 的数据；bw=240224KB/s 代表顺序写的速率为 234MB/s；iops=234 代表顺序写 IOPS 或者说顺序写吞吐量为 234；runt=  4365msec 代表用时 4ms。

#### 测试顺序读 IOPS

```
root@Lab:/home/tiger# fio -direct=1 -iodepth=64 -rw=read -ioengine=libaio -bs=1024k -size=1G -numjobs=1 -runtime=1000 -group_reporting -filename=/dev/dm-0 -name=Read_PPS_Testing

# 结果
Read_PPS_Testing: (g=0): rw=read, bs=1M-1M/1M-1M/1M-1M, ioengine=libaio, iodepth=64
fio-2.1.3
Starting 1 process
Jobs: 1 (f=1)
Read_PPS_Testing: (groupid=0, jobs=1): err= 0: pid=2777: Mon Jun  4 16:08:42 2018
  read : io=1024.0MB, bw=967321KB/s, iops=944, runt=  1084msec
    slat (usec): min=47, max=28526, avg=855.71, stdev=1958.91
    clat (msec): min=9, max=230, avg=65.31, stdev=42.75
     lat (msec): min=10, max=230, avg=66.18, stdev=43.17
    clat percentiles (msec):
     |  1.00th=[   14],  5.00th=[   21], 10.00th=[   24], 20.00th=[   30],
     | 30.00th=[   36], 40.00th=[   40], 50.00th=[   50], 60.00th=[   61],
     | 70.00th=[   84], 80.00th=[  110], 90.00th=[  133], 95.00th=[  147],
     | 99.00th=[  172], 99.50th=[  192], 99.90th=[  231], 99.95th=[  231],
     | 99.99th=[  231]
    bw (KB  /s): min=923648, max=1032094, per=100.00%, avg=977871.00, stdev=76682.90
    lat (msec) : 10=0.10%, 20=4.49%, 50=45.70%, 100=25.98%, 250=23.73%
  cpu          : usr=3.69%, sys=79.41%, ctx=87, majf=0, minf=551
  IO depths    : 1=0.1%, 2=0.2%, 4=0.4%, 8=0.8%, 16=1.6%, 32=3.1%, >=64=93.8%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=99.9%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued    : total=r=1024/w=0/d=0, short=r=0/w=0/d=0

Run status group 0 (all jobs):
   READ: io=1024.0MB, aggrb=967321KB/s, minb=967321KB/s, maxb=967321KB/s, mint=1084msec, maxt=1084msec

Disk stats (read/write):
    dm-0: ios=1968/0, merge=0/0, ticks=68064/0, in_queue=73904, util=90.10%, aggrios=2048/0, aggrmerge=0/0, aggrticks=84940/0, aggrin_queue=84884, aggrutil=89.33%
  sda: ios=2048/0, merge=0/0, ticks=84940/0, in_queue=84884, util=89.33%
```

重点看到 `read : io=1024.0MB, bw=967321KB/s, iops=944, runt=  1084msec`，io=1024.0MB 代表顺序读了 1GB 的数据；bw=967321KB/s 代表顺序读的速率为 945MB/s；iops=944 代表顺序读 IOPS 或者说顺序读吞吐量为 944；runt=  1084msec 代表用时 1ms。

> 该测试磁盘的吞吐量约等于 700

#### fio 部分参数解析

- -direct=1：测试时忽略 I/O 缓存，数据直写磁盘，让测试结果更能体现磁盘本身的性能
- -iodepth=128：同时发出 I/O 个数的上线为 128
- -rw=randwrite：测试时的读写策略为随机写，其他取值分别是 [randread（随机读random reads）, read（顺序读sequential reads）, write（顺序写sequential writes）, randrw（混合随机读写mixed random reads and writes）]
- -ioengine=libaio：表示使用 Linux AIO
- -bs=4k：单次 I/O 的块文件大小为 4KB，适用于测试随机读写，当测试顺序读写是需要调大该值，比如 1024KB
- -size=1G：测试文件大小为 1GB
- -numjobs=1：测试线程数为 1
- -runtime=1000：测试限时 1000s 内完成
- -filename：带测试的磁盘对应的设备名

#### 测试延迟

```
root@ubuntu:~# ioping /dev/dm-0 -c 10
4.0 KiB from /dev/dm-0 (device 62.8 GiB): request=1 time=318 us
4.0 KiB from /dev/dm-0 (device 62.8 GiB): request=2 time=1.3 ms
4.0 KiB from /dev/dm-0 (device 62.8 GiB): request=3 time=285 us
4.0 KiB from /dev/dm-0 (device 62.8 GiB): request=4 time=535 us
4.0 KiB from /dev/dm-0 (device 62.8 GiB): request=5 time=959 us
4.0 KiB from /dev/dm-0 (device 62.8 GiB): request=6 time=1.9 ms
4.0 KiB from /dev/dm-0 (device 62.8 GiB): request=7 time=349 us
4.0 KiB from /dev/dm-0 (device 62.8 GiB): request=8 time=1.4 ms
4.0 KiB from /dev/dm-0 (device 62.8 GiB): request=9 time=291 us
4.0 KiB from /dev/dm-0 (device 62.8 GiB): request=10 time=307 us

--- /dev/dm-0 (device 62.8 GiB) ioping statistics ---
10 requests completed in 9.0 s, 1.3 k iops, 5.1 MiB/s
min/avg/max/mdev = 285 us / 764 us / 1.9 ms / 554 us
```

重点看到 `min/avg/max/mdev = 285 us / 764 us / 1.9 ms / 554 us`，磁盘的最小延迟为 285us，平均延迟为 764us，最大延迟为 1.9 ms (其中，1s = 1000ms；1ms = 1000us)。

---

需要注意的是这里的测试是裸盘测试，也就是只针对磁盘硬件的测试。比如随机读的 IOPS 测试结果是 47MB/s 指的是磁盘本身每秒能随机读 47MB 的数据，在实际场景中，还要考虑加上数据库之后的随机读写，加上文件 I/O 之后的随机读写等。
