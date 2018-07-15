下面的讨论都是基于 ANSI SQL 的标准，不同的数据库之间的具体实现会有一点出入，但是大体上一致。

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

# 数据建模

- 实体：指的是业务逻辑中涉及到的需要记录下来的人、事、物。在建立实体时，除了业务上显而易见的字段，往往还需要想细一点 (可能是技术上需要的字段、可能是业务逻辑上不明显的字段)，确保字段的完整。特别需要注意的是实体中的字段应该要符合第一范式，即不可再拆分
- 关系：指的是不同实体之间的对应关系，有这么几种：没关系、一对一、一对多、多对多。其中，一对一的情况下，外键建在那个表都没有大问题；一对多的情况下，外键必然在 “多” 的那种表上；多对多的情况下，需要第三张表来存放这种关系
- E-R 图：有需要的可以维护一章，不过个人实践中发现直接在代码的 ORM 模型中添加适当的注视说明，会更加省心有效
- 反范式：不太推荐在关系型数据库里面使用反范式，既然用了关系型数据库，图的就是 “关系” 这一点，如果过多的反范式，那倒不如将那部分的数据转移到非关系型数据库上，或者用好缓存去解决。

> 总的来说，数据建模阶段应该要紧跟业务逻辑，可以通过和产品面谈，仔细研究原型图、设计图等方式尽可能地做到不漏实体、不漏字段、不错关系

# 表结构设计

- 表的命名
  - 使用名词作为表名。比如消费记录，consumption 比 consume 要好些
  - 相关的表使用统一的前缀。比如 member, member_wechat
- 字段的命名
  - 优先用名词。比如邀请人数 invitation_number 比 invite_number 好，实在是动词的，可以使用动词的过去分词形式
  - 关于时间的字段，一般时间相关的字段会涉及到某个动作，推荐使用动词的过去分词加 in, at。比如创建时间 created_at，过期时间 expired_in，有着明显的代表未来的时间点可以优先用 in
  - 尽量用单数。如果需要复数，需要考虑是否可以使用枚举类型，或者是否数据建模有问题，这个 “多” 没有单独成一个表













