记录用 `pg_basebackup` 搭建流复制环境的过程。

# 环境信息

- 物理设备：笔记本虚拟机
- 系统：ubuntu 14.04
- PG 版本：PostgreSQL 9.6
- 主库 IP：192.168.1.36
- 备库IP： 192.168.1.35

# 主库上操作

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

