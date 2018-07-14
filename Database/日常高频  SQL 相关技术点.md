下面记录的都是基于 ANSI SQL 的标准，不同的数据库之间的具体实现会有一点出入，但是大体上一致。

# SQL

## 增加

- 最常见

  ```
  INSERT INTO $table($field1, $field2, ...) VALUES($value1, $value2, ...);
  ```
  
- 从查询结果中获取 value
  
  ```
  INSERT INTO $table1($field1, $field2, ...) SELECT $field1, $field2, ... FROM $table2;
  ```

## 删除/修改

- 一定不要忘了带上 `WHERE` 子句
- 在做这两个操作之前最好先备份数据，或者在测试数据库中测过没问题先
- 实际开发中不推荐真正的删除操作，可以使用逻辑删除代替

## 查询

- self join，单张表自身的 join 操作。比如有一张会员表 member，里面记录着每个人的姓名和公司信息，现在要查询跟 tiger 同一家公司的人员名单

  ```
  SELECT m2.name, m2.company FROM member as m1, member as m2  WHERE m1.name = 'tiger' and m1.company = m2.company;
  ```
  
- inner join，两张以上的表 join 操作。比如订单表 order 和会员表 member，且订单表中有记录着对应会员的 id，现在要查询下过订单的会员

  ```
  SELECT member.name, order.number FROM member INNER JOIN order ON member.id = order.member_id;
  ```

- left outer join，两张表以上的 join 操作，且右边的表就算没有关联行也返回。同 inner join，现在要查询所有会员的订单情况，包括没有下过单的会员

  ```
  SELECT member.name, order.number FROM member LEFT OUTER JOIN order ON member.id = order.member_id;
  ```

- right outer join，两张表以上的 join 操作，且左边的表就算没有关联行也返回。就是跟 left outer join 相反。

# 操纵表

## 创建

```
CREATE TABLE $table
(
  $filed1 约束 (可选),
  $filed2 约束 (可选),
  ...
);
```

## 删除

```
DROP TABLE $table;
```

## 修改

- 增加字段

  ```
  ALERT TABLE $table ADD $filed 约束 (可选);
  ```

- 删除字段

  ```
  ALERT TABLE $table DROP CLOUMN $filed;
  ```

# 统计函数

- COUNT(*)/COUNT($filed)：统计行数/统计特定值的列的数量
- MAX($filed)：统计某个列的最大值
- MIN($filed)：统计某个列的最小值
- SUM($filed)：统计某个列的总和
- AVG($filed)：统计某个列的平局值

# 分组 GROUP BY

- `GROUP BY` 通常配合统计函数使用
- `GROUP BY` 下的过滤应该使用 `HAVING`
- `WHERE` 子句的语法都适用于  `HAVING` 子句

# SELECT 子句的顺序

1. SELECT
2. FROM
3. WHERE
4. GROUP BY
5. HAVING
6. ORDER BY
















