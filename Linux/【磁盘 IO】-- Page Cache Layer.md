在日常维护服务器时，使用 `free` 命令会发现 free 字段会随着运行的时间增加而不断变小，而 cache 字段会随着运行的时间增加而不断变大。

```
root@ubuntu:/proc/sys/vm# free -m
             total       used       free     shared    buffers     cached
Mem:           990        872        117          0        155        531
-/+ buffers/cache:        185        805
Swap:            0          0          0
```

这其实是因为 Page Cache 机制导致的。简单来说，如果没有该机制，上层发出的 I/O 请求就会直接落到磁盘设备上，这对于磁盘这种慢设备来说简直是灾难。正是因为有 Page Cache 的存在，大量的 I/O 请求可以在到达 Page Cache Layer 之后就能返回，而无需真正请求磁盘。

当进程第一次读取某个数据块时，只能直接从磁盘读取，然后内核会向 Page Cache Layer 申请适当的页来缓存读取到的数据块，当有进程需要再次读取之前的数据块时，就会调用 read() 函数，此时 read() 函数通过虚拟内存机制访问到 Page Cache Layer 中缓存好的页，也就避免了对磁盘的 I/O 操作了。Page Cache Layer 即是磁盘子系统的一部分，也是联系内存子系统和磁盘子系统的枢纽，Page Cache Layer 存在于物理内存中，因此既需要和虚拟内存机制协作，又需要和下层文件系统协作。

对于进程来说，如果调用 read() 时缓存命中，I/O 请求就会从 Page Cache Layer 中获取到数据并返回给进程；如果调用 write() 时没有指定要直接写磁盘，I/O 请求就会往 Page Cache Layer 的缓冲区中写入数据，等到缓冲区满了之后，再一次性地将数据写入磁盘。可以看到，Page Cache Layer 让高速的内存暂时替代了低速的磁盘 (前提是缓存命中和缓存写模式)，同时还减少了对磁盘实质的 I/O 操作，降低了磁盘的负担，大大滴提升了磁盘子系统的性能。

