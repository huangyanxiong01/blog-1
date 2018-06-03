### <font color=#00b0f0>简介</font>

`iostat` 是 Linux 下最基本的 I/O 设备性能工具，它提供的信息比较丰富且个别字段的意义很容易混淆。

---

### <font color=#00b0f0>运行环境</font>

```
# uname -a
Linux ubuntu 3.16.0-30-generic #40~14.04.1-Ubuntu SMP Thu Jan 15 17:43:14 UTC 2015 x86_64 x86_64 x86_64 GNU/Linux

# python2 --version
Python 2.7.9

# cat /etc/*-release
DISTRIB_DESCRIPTION="Ubuntu 14.04.2 LTS"
```

---

### <font color=#00b0f0>字段的意义</font>

`iostat` 的输出分两部分，第一部分是 CPU 的报告，第二部分是 I/O 设备的报告，下面重点看第二部分

```
root@ubuntu:/opt# iostat -xmtp 3
Linux 3.16.0-30-generic (ubuntu) 	05/31/2018 	_x86_64_	(2 CPU)

05/31/2018 10:04:45 AM
avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           4.85    0.00   27.47   15.98    0.00   51.71

Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
sda               0.00     2.00    0.00 7135.00     0.00    27.88     8.00     0.80    0.11    0.00    0.11   0.11  79.60
sda1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sda2              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sda5              0.00     2.00    0.00 7134.67     0.00    27.88     8.00     0.80    0.11    0.00    0.11   0.11  79.60
dm-0              0.00     0.00    0.00 7136.67     0.00    27.88     8.00     0.78    0.11    0.00    0.11   0.11  77.87
dm-1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00

...
```

- Device：对应 `/dev` 目录下的的设备 (加了 `-p` 参数会显示设备的分区，如 `sda1`)

