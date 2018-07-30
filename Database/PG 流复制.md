记录用 `pg_basebackup` 搭建流复制环境的过程。

# 环境信息

- 物理设备：笔记本虚拟机
- 系统：ubuntu 14.04
- PG 版本：PostgreSQL 9.6
- 主库 IP：192.168.1.36
- 备库IP： 192.168.1.35

# 主库操作

1. 创建复制用户

```
CREATE USER repuser
REPLICATION 
LOGIN
CONNECTION LIMIT 2
ENCRYPTED PASSWORD 'rep123us345er';
```

2. 设置 pg_hba.conf，添加以下

```
host   replication     repuser          192.168.1.35/32         md5
```

3. 设置主库 postgresql.conf

```
checkpoint_segments = 16
archive_mode = on
archive_command = '/bin/date'
max_wal_senders = 3
wal_keep_segments = 16 
max_wal_senders = 3
```

4. 重载配置文件

```
> pg_ctl reload -D $PGDATA
server signaled
```

5. 查看表空间目录
```
postgres=# \db
                      List of tablespaces
     Name      |  Owner   |              Location               
---------------+----------+-------------------------------------
 pg_default    | postgres | 
 pg_global     | postgres | 
 tbs_francs    | postgres | /database/pg93/pg_tbs/tbs_francs
 tbs_source_db | postgres | /database/pg93/pg_tbs/tbs_source_db
(4 rows)

```

6. 查看数据目录

```
> echo $PGDATA
/database/pg93/pg_root
```

# 备库操作

1. 创建目录并赋权

```
> mkdir -p /database/pg93/pg_tbs/tbs_francs
> mkdir -p /database/pg93/pg_tbs/tbs_source_db
> mkdir -p /database/pg93/pg_root

> chown -R pg93:pg93 /database/pg93/pg_tbs/tbs_francs
> chown -R pg93:pg93 /database/pg93/pg_tbs/tbs_source_db
> chown -R pg93:pg93 /database/pg93/pg_root
> chmod 0700 /database/pg93/pg_root
```

2. 创建 .pgpass

```
> cat .pgpass
192.168.1.36:1925:replication:repuser:rep123us345er

> chmod 0600 .pgpass
```

3. 使用 pg_basebackup 生成备库

```
> pg_basebackup -D /database/pg93/pg_root -Fp -Xs -v -P -h 192.168.1.36 -p 1925 -U repuser

transaction log start point: 1/1B000024 on timeline 1
pg_basebackup: starting background WAL receiver
651493/651493 kB (100%), 3/3 tablespaces                                         
transaction log end point: 1/1B0000DC
pg_basebackup: waiting for background process to finish streaming ...
pg_basebackup: base backup completed
```
