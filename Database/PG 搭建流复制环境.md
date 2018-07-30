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

4. 设置从库 postgresql.conf 

```
hot_standby = on
```

5. 创建从库 recovery.conf

```
> cp /opt/pgsql9.3beta1/share/recovery.conf.sample  recovery.conf
```

6. 修改以下参数

```
standby_mode = on
primary_conninfo = 'host=192.168.1.36 port=1925 user=repuser'
trigger_file = '/database/pg93/pg_root/postgresql.trigger.1925'
```

7. 启动从库服务

```
> pg_ctl start -D $PGDATA
server starting
```

8. 查看备库进程

```
> ps -ef | grep pg93
pg93     31398     1  0 21:09 pts/0    00:00:00 /opt/pgsql9.3beta1/bin/postgres -D /database/pg93/pg_root
pg93     31399 31398  0 21:09 ?        00:00:00 postgres: logger process                                 
pg93     31400 31398  0 21:09 ?        00:00:00 postgres: startup process   waiting for 00000001000000010000001A
pg93     31401 31398  0 21:09 ?        00:00:00 postgres: checkpointer process                           
pg93     31402 31398  0 21:09 ?        00:00:00 postgres: writer process                                 
pg93     31403 31398  0 21:09 ?        00:00:00 postgres: stats collector process                        
pg93     31404 31398  0 21:09 ?        00:00:00 postgres: wal receiver process
```

9. 登录到主库所在的服务器，查看主库进程

```
> ps -ef | grep pg93
pg93      2504     1  0 Jun28 ?        00:00:26 /opt/pgsql9.3beta1/bin/postgres -D /database/pg93/pg_root
pg93      2505  2504  0 Jun28 ?        00:00:00 postgres: logger process                                 
pg93      2507  2504  0 Jun28 ?        00:00:08 postgres: checkpointer process                           
pg93      2508  2504  0 Jun28 ?        00:00:28 postgres: writer process                                 
pg93      2509  2504  0 Jun28 ?        00:00:08 postgres: wal writer process                             
pg93      2510  2504  0 Jun28 ?        00:00:19 postgres: autovacuum launcher process                    
pg93      2511  2504  0 Jun28 ?        00:00:00 postgres: archiver process   last was 000000010000000100000019.00000024.backup
pg93      2512  2504  0 Jun28 ?        00:00:44 postgres: stats collector process                        
pg93     31898  2504  0 21:09 ?        00:00:00 postgres: wal sender process repuser 192.168.1.35(39545) idle
```

# 测试

1. 登录到主库服务器执行

```
> psql
psql (9.3beta1)
Type "help" for help.

postgres=# create table test_1 (id int4,create_time timestamp(0) without time zone);
CREATE TABLE

postgres=# insert into test_1 values (1,now());
INSERT 0 1

postgres=# select * from test_1;
 id |     create_time     
----+---------------------
  1 | 2013-07-01 21:15:34
(1 row)
```

2. 登录到备库服务器执行

```
> psql
psql (9.3beta1)
Type "help" for help.

postgres=# select * from test_1 

postgres=# select * from test_1 ;
 id |     create_time     
----+---------------------
  1 | 2013-07-01 21:15:34
(1 row)

```

> 可以看到主从的数据已经同步

# 其他






