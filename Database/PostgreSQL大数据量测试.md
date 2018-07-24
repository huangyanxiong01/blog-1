# 硬件配置
- 2核
- 4g

# 表
- user
- admin
- space
- order
> admin_id 作为外键在 space 表

> user_id、space_id 作为外键在 order表

# 1w单
- user_id：fee705cd-6603-4a57-99fb-8e8464ce321c

- space_id：0ad17363-d58b-4dc9-9e6f-680c3b4eac56

# 3w单
- user_id: cbb812ca-da84-4858-9911-e66008742ec4
- space_id: b3906249-cdd7-4cbe-9969-97cecaa16951

# 100w数据量
## 无索引
```
herelywork_db=# explain analyze select * from "order";
                                                     QUERY PLAN                                                      
---------------------------------------------------------------------------------------------------------------------
 Seq Scan on "order"  (cost=0.00..63154.44 rows=1222344 width=290) (actual time=0.088..233.945 rows=1222343 loops=1)
 Planning time: 0.085 ms
 Execution time: 324.572 ms
(3 rows)
```

>结论：100w级别的数据量，就算没有索引，PostgreSQL的查询性能还是很好的。

# 600w数据量
## 无索引
```
herelywork_db=# explain analyze select * from "order";
                                                      QUERY PLAN                                                       
-----------------------------------------------------------------------------------------------------------------------
 Seq Scan on "order"  (cost=0.00..315142.61 rows=6099561 width=290) (actual time=0.469..9045.487 rows=6099526 loops=1)
 Planning time: 12.281 ms
 Execution time: 9698.843 ms
(3 rows)
```

```
herelywork_db=# explain analyze select * from "order" where user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c';
                                                     QUERY PLAN                                                     
--------------------------------------------------------------------------------------------------------------------
 Seq Scan on "order"  (cost=0.00..330391.51 rows=11183 width=290) (actual time=29.788..8543.899 rows=10001 loops=1)
   Filter: (user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c'::uuid)
   Rows Removed by Filter: 6089525
 Planning time: 2.941 ms
 Execution time: 8544.965 ms
(5 rows)
```

```
explain analyze select * from "order" where space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951';
                                                     QUERY PLAN                                                     
--------------------------------------------------------------------------------------------------------------------
 Seq Scan on "order"  (cost=0.00..332016.08 rows=1 width=290) (actual time=12512.709..12541.763 rows=30001 loops=1)
   Filter: (space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951'::uuid)
   Rows Removed by Filter: 6099525
 Planning time: 0.117 ms
 Execution time: 12544.016 ms
(5 rows)

herelywork_db=# explain analyze select * from "order" where space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951';
                                                    QUERY PLAN                                                    
------------------------------------------------------------------------------------------------------------------
 Seq Scan on "order"  (cost=0.00..332016.08 rows=1 width=290) (actual time=7200.917..7209.551 rows=30001 loops=1)
   Filter: (space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951'::uuid)
   Rows Removed by Filter: 6099525
 Planning time: 1.439 ms
 Execution time: 7211.817 ms
(5 rows)
```

>结论：600w级别数据量，必须要加索引了。

## 索引
> 索引加到 user_id 和 space_id

> 600w数据量级别下，加索引的时间约为14秒，添加普通索引：create index space_id_idx on "order" (space_id);

> 注意：PostgreSQL 本身存在缓存机制，所以同一条查询 SQL 执行多次时，会越来越快，如下所示。

- index => primery_key

```
herelywork_db=# explain analyze select * from "order" where id = 'fd80e524-de18-42d8-919e-0faf0e3cc7ab';
                                                      QUERY PLAN                                                      
----------------------------------------------------------------------------------------------------------------------
 Index Scan using order_pkey on "order"  (cost=0.43..8.45 rows=1 width=290) (actual time=6.968..6.970 rows=1 loops=1)
   Index Cond: (id = 'fd80e524-de18-42d8-919e-0faf0e3cc7ab'::uuid)
 Planning time: 1.533 ms
 Execution time: 7.107 ms
(4 rows)

herelywork_db=# explain analyze select * from "order" where id = 'fd80e524-de18-42d8-919e-0faf0e3cc7ab';
                                                      QUERY PLAN                                                      
----------------------------------------------------------------------------------------------------------------------
 Index Scan using order_pkey on "order"  (cost=0.43..8.45 rows=1 width=290) (actual time=0.050..0.051 rows=1 loops=1)
   Index Cond: (id = 'fd80e524-de18-42d8-919e-0faf0e3cc7ab'::uuid)
 Planning time: 0.103 ms
 Execution time: 0.092 ms
(4 rows)

herelywork_db=# explain analyze select * from "order" where id = 'fd80e524-de18-42d8-919e-0faf0e3cc7ab';
                                                      QUERY PLAN                                                      
----------------------------------------------------------------------------------------------------------------------
 Index Scan using order_pkey on "order"  (cost=0.43..8.45 rows=1 width=290) (actual time=0.024..0.025 rows=1 loops=1)
   Index Cond: (id = 'fd80e524-de18-42d8-919e-0faf0e3cc7ab'::uuid)
 Planning time: 0.167 ms
 Execution time: 0.066 ms
(4 rows)
```

- index => user_id

```
herelywork_db=# explain analyze  select * from "order" where user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c';
                                                          QUERY PLAN                                                          
------------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=263.52..37543.11 rows=11237 width=290) (actual time=0.878..4.292 rows=10001 loops=1)
   Recheck Cond: (user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c'::uuid)
   Heap Blocks: exact=419
   ->  Bitmap Index Scan on user_id_idx  (cost=0.00..260.71 rows=11237 width=0) (actual time=0.821..0.821 rows=10001 loops=1)
         Index Cond: (user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c'::uuid)
 Planning time: 13.989 ms
 Execution time: 5.629 ms
(7 rows)
```

- index => space_id

```
explain analyze select * from "order" where space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951';
                                                          QUERY PLAN                                                           
-------------------------------------------------------------------------------------------------------------------------------
 Index Scan using space_id_idx on "order"  (cost=0.43..8.45 rows=1 width=290) (actual time=3.367..1117.992 rows=30001 loops=1)
   Index Cond: (space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951'::uuid)
 Planning time: 14.997 ms
 Execution time: 1122.665 ms
(4 rows)

herelywork_db=# explain analyze select * from "order" where space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951';
                                                         QUERY PLAN                                                          
-----------------------------------------------------------------------------------------------------------------------------
 Index Scan using space_id_idx on "order"  (cost=0.43..8.45 rows=1 width=290) (actual time=0.076..10.386 rows=30001 loops=1)
   Index Cond: (space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951'::uuid)
 Planning time: 0.153 ms
 Execution time: 12.721 ms
(4 rows)
```

# 1000w数据量
## 无索引

```
herelywork_db=# explain analyze select * from "order";
                                                       QUERY PLAN                                                        
-------------------------------------------------------------------------------------------------------------------------
 Seq Scan on "order"  (cost=0.00..525534.71 rows=10171671 width=290) (actual time=0.007..9350.365 rows=10171640 loops=1)
 Planning time: 1.172 ms
 Execution time: 10610.636 ms
(3 rows)
```

```
explain analyze select * from "order" order by date_created limit 1;
                                                             QUERY PLAN                                                              
-------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=576393.06..576393.07 rows=1 width=290) (actual time=8408.656..8408.659 rows=1 loops=1)
   ->  Sort  (cost=576393.06..601822.24 rows=10171671 width=290) (actual time=8407.645..8407.645 rows=1 loops=1)
         Sort Key: date_created
         Sort Method: top-N heapsort  Memory: 25kB
         ->  Seq Scan on "order"  (cost=0.00..525534.71 rows=10171671 width=290) (actual time=0.003..6341.299 rows=10171640 loops=1)
 Planning time: 0.536 ms
 Execution time: 8410.364 ms
(7 rows)
```

## 索引

> index => 3w单 space_id

```
herelywork_db=# explain analyze select * from "order" where space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951';
                                                          QUERY PLAN                                                           
-------------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=828.81..98403.13 rows=31532 width=290) (actual time=7.496..101.589 rows=30001 loops=1)
   Recheck Cond: (space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951'::uuid)
   Heap Blocks: exact=1251
   ->  Bitmap Index Scan on space_id_idx  (cost=0.00..820.92 rows=31532 width=0) (actual time=6.399..6.399 rows=30001 loops=1)
         Index Cond: (space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951'::uuid)
 Planning time: 14.073 ms
 Execution time: 105.098 ms
(7 rows)

herelywork_db=# explain analyze select * from "order" where space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951';
                                                          QUERY PLAN                                                           
-------------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=828.81..98403.13 rows=31532 width=290) (actual time=3.083..8.370 rows=30001 loops=1)
   Recheck Cond: (space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951'::uuid)
   Heap Blocks: exact=1251
   ->  Bitmap Index Scan on space_id_idx  (cost=0.00..820.92 rows=31532 width=0) (actual time=2.900..2.900 rows=30001 loops=1)
         Index Cond: (space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951'::uuid)
 Planning time: 0.254 ms
 Execution time: 10.853 ms
(7 rows)

herelywork_db=# explain analyze select * from "order" where space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951';
                                                          QUERY PLAN                                                           
-------------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=828.81..98403.13 rows=31532 width=290) (actual time=3.024..8.703 rows=30001 loops=1)
   Recheck Cond: (space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951'::uuid)
   Heap Blocks: exact=1251
   ->  Bitmap Index Scan on space_id_idx  (cost=0.00..820.92 rows=31532 width=0) (actual time=2.852..2.852 rows=30001 loops=1)
         Index Cond: (space_id = 'b3906249-cdd7-4cbe-9969-97cecaa16951'::uuid)
 Planning time: 0.115 ms
 Execution time: 11.248 ms
(7 rows)
```

> index => 1w单 space_id

```
herelywork_db=# explain analyze select * from "order" where space_id = '0ad17363-d58b-4dc9-9e6f-680c3b4eac56';
                                                          QUERY PLAN                                                          
------------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=243.39..32617.18 rows=9155 width=290) (actual time=6.877..28.680 rows=10001 loops=1)
   Recheck Cond: (space_id = '0ad17363-d58b-4dc9-9e6f-680c3b4eac56'::uuid)
   Heap Blocks: exact=419
   ->  Bitmap Index Scan on space_id_idx  (cost=0.00..241.10 rows=9155 width=0) (actual time=6.002..6.002 rows=10001 loops=1)
         Index Cond: (space_id = '0ad17363-d58b-4dc9-9e6f-680c3b4eac56'::uuid)
 Planning time: 0.379 ms
 Execution time: 30.251 ms
(7 rows)

herelywork_db=# explain analyze select * from "order" where space_id = '0ad17363-d58b-4dc9-9e6f-680c3b4eac56';
                                                          QUERY PLAN                                                          
------------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=243.39..32617.18 rows=9155 width=290) (actual time=1.765..4.304 rows=10001 loops=1)
   Recheck Cond: (space_id = '0ad17363-d58b-4dc9-9e6f-680c3b4eac56'::uuid)
   Heap Blocks: exact=419
   ->  Bitmap Index Scan on space_id_idx  (cost=0.00..241.10 rows=9155 width=0) (actual time=1.657..1.657 rows=10001 loops=1)
         Index Cond: (space_id = '0ad17363-d58b-4dc9-9e6f-680c3b4eac56'::uuid)
 Planning time: 0.307 ms
 Execution time: 5.402 ms
(7 rows)

herelywork_db=# explain analyze select * from "order" where space_id = '0ad17363-d58b-4dc9-9e6f-680c3b4eac56';
                                                          QUERY PLAN                                                          
------------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=243.39..32617.18 rows=9155 width=290) (actual time=1.416..3.350 rows=10001 loops=1)
   Recheck Cond: (space_id = '0ad17363-d58b-4dc9-9e6f-680c3b4eac56'::uuid)
   Heap Blocks: exact=419
   ->  Bitmap Index Scan on space_id_idx  (cost=0.00..241.10 rows=9155 width=0) (actual time=1.324..1.324 rows=10001 loops=1)
         Index Cond: (space_id = '0ad17363-d58b-4dc9-9e6f-680c3b4eac56'::uuid)
 Planning time: 0.146 ms
 Execution time: 4.319 ms
(7 rows)
```

> index => 3w单 user_id

```
herelywork_db=# explain analyze select * from "order" where user_id = 'cbb812ca-da84-4858-9911-e66008742ec4'; 
                                                          QUERY PLAN                                                          
------------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=828.81..98403.13 rows=31532 width=290) (actual time=9.794..16.438 rows=30001 loops=1)
   Recheck Cond: (user_id = 'cbb812ca-da84-4858-9911-e66008742ec4'::uuid)
   Heap Blocks: exact=1251
   ->  Bitmap Index Scan on user_id_idx  (cost=0.00..820.92 rows=31532 width=0) (actual time=9.609..9.609 rows=30001 loops=1)
         Index Cond: (user_id = 'cbb812ca-da84-4858-9911-e66008742ec4'::uuid)
 Planning time: 0.122 ms
 Execution time: 19.047 ms
(7 rows)

herelywork_db=# explain analyze select * from "order" where user_id = 'cbb812ca-da84-4858-9911-e66008742ec4';
                                                          QUERY PLAN                                                          
------------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=828.81..98403.13 rows=31532 width=290) (actual time=4.216..9.482 rows=30001 loops=1)
   Recheck Cond: (user_id = 'cbb812ca-da84-4858-9911-e66008742ec4'::uuid)
   Heap Blocks: exact=1251
   ->  Bitmap Index Scan on user_id_idx  (cost=0.00..820.92 rows=31532 width=0) (actual time=3.993..3.993 rows=30001 loops=1)
         Index Cond: (user_id = 'cbb812ca-da84-4858-9911-e66008742ec4'::uuid)
 Planning time: 0.212 ms
 Execution time: 11.836 ms
(7 rows)

herelywork_db=# explain analyze select * from "order" where user_id = 'cbb812ca-da84-4858-9911-e66008742ec4';
                                                          QUERY PLAN                                                          
------------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=828.81..98403.13 rows=31532 width=290) (actual time=3.304..8.854 rows=30001 loops=1)
   Recheck Cond: (user_id = 'cbb812ca-da84-4858-9911-e66008742ec4'::uuid)
   Heap Blocks: exact=1251
   ->  Bitmap Index Scan on user_id_idx  (cost=0.00..820.92 rows=31532 width=0) (actual time=3.139..3.139 rows=30001 loops=1)
         Index Cond: (user_id = 'cbb812ca-da84-4858-9911-e66008742ec4'::uuid)
 Planning time: 0.105 ms
 Execution time: 11.775 ms
(7 rows)
```

> index => 1w单 user_id

```
herelywork_db=# explain analyze select * from "order" where user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c';
                                                         QUERY PLAN                                                          
-----------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=243.39..32617.18 rows=9155 width=290) (actual time=7.178..9.178 rows=10001 loops=1)
   Recheck Cond: (user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c'::uuid)
   Heap Blocks: exact=419
   ->  Bitmap Index Scan on user_id_idx  (cost=0.00..241.10 rows=9155 width=0) (actual time=5.632..5.632 rows=10001 loops=1)
         Index Cond: (user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c'::uuid)
 Planning time: 0.275 ms
 Execution time: 10.011 ms
(7 rows)

herelywork_db=# explain analyze select * from "order" where user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c';
                                                         QUERY PLAN                                                          
-----------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=243.39..32617.18 rows=9155 width=290) (actual time=1.143..3.535 rows=10001 loops=1)
   Recheck Cond: (user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c'::uuid)
   Heap Blocks: exact=419
   ->  Bitmap Index Scan on user_id_idx  (cost=0.00..241.10 rows=9155 width=0) (actual time=1.075..1.075 rows=10001 loops=1)
         Index Cond: (user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c'::uuid)
 Planning time: 0.087 ms
 Execution time: 4.693 ms
(7 rows)

herelywork_db=# explain analyze select * from "order" where user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c';
                                                         QUERY PLAN                                                          
-----------------------------------------------------------------------------------------------------------------------------
 Bitmap Heap Scan on "order"  (cost=243.39..32617.18 rows=9155 width=290) (actual time=1.913..3.687 rows=10001 loops=1)
   Recheck Cond: (user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c'::uuid)
   Heap Blocks: exact=419
   ->  Bitmap Index Scan on user_id_idx  (cost=0.00..241.10 rows=9155 width=0) (actual time=1.728..1.728 rows=10001 loops=1)
         Index Cond: (user_id = 'fee705cd-6603-4a57-99fb-8e8464ce321c'::uuid)
 Planning time: 0.350 ms
 Execution time: 4.562 ms
(7 rows)
```

> 结论：1000w数据量情况下，PostgreSQL 的索引性能表现优秀。

# 最终数据量统计

> 数据库herelywork

```
herelywork_db=# select pg_database_size(current_database());
 pg_database_size 
------------------
      24219774740
(1 row)
```

```
postgres=# \l+
                                                                 List of databases
     Name      |  Owner   | Encoding  | Collate | Ctype |   Access privileges   |  Size   | Tablespace |                Description                 
---------------+----------+-----------+---------+-------+-----------------------+---------+------------+--------------------------------------------
 herely_db     | postgres | SQL_ASCII | C       | C     |                       | 7753 kB | pg_default | 
 herelywork_db | postgres | SQL_ASCII | C       | C     |                       | 23 GB   | pg_default | 
 postgres      | postgres | SQL_ASCII | C       | C     |                       | 6532 kB | pg_default | default administrative connection database
 template0     | postgres | SQL_ASCII | C       | C     | =c/postgres          +| 6409 kB | pg_default | unmodifiable empty database
               |          |           |         |       | postgres=CTc/postgres |         |            | 
 template1     | postgres | SQL_ASCII | C       | C     | =c/postgres          +| 6417 kB | pg_default | default template for new databases
               |          |           |         |       | postgres=CTc/postgres |         |            | 
(5 rows)
```

> "order" 表（单表1000多w）

```
herelywork_db=# select pg_relation_size('order');
 pg_relation_size 
------------------
       3471917056
(1 row)
```

> "user" 表（单表1000多w）

```
herelywork_db=# select pg_relation_size('user');
 pg_relation_size 
------------------
       4611014656
(1 row)
```

> "admin" 表（单表1000多w）

```
herelywork_db=# select pg_relation_size('admin');
 pg_relation_size 
------------------
       4611014656
(1 row)
```

> 结论：表的大小虽然只有12g左右，但是数据库的大小却有23g左右，因为还包括一些索引等其他需要储存的数据。
