# 导引

CI 代表持续集成，CD 代表持续交付或持续部署。个人认为，这是一种能比较好地将产品、开发、测试、运维等人员联系在一起，形成一条代码流水线，且同时强调自动化的现代软件工程方法。

对于旧的瀑布开发模型来说，有几个比较大的缺陷：

- 对于开发和测试：开发完了才进行测试，返工量会集中在一个短的时间端内。结果是开发要在短时间内大量地返工，开发觉得自己很苦逼，测试觉得开发很傻逼
- 对于开发和运维：开发完了，测试完了才第一次集成到某个环境上，报错会集中在一个短的时间段内，而且产品经理在这第一次的试用中也会发现很多的问题。结果是短时间内运维忙得要死，开发要大量地返工，测试也要跟着改，运维觉得自己很苦逼，开发觉得运维和产品很傻逼，测试觉得开发很傻逼

> 总的来说就是集成太慢，导致各个工种之间反馈太慢，最终容易产生鄙视链和相互甩锅。

# 方法

## 几幅图片

跟其他的计算机知识一样，CI&CD 也是可以划分层次的，但是跟 TCP/IP、[磁盘 I/O](https://github.com/hsxhr-10/blog/blob/master/Linux/【磁盘%20IO】--%207%20层模型.md) 等分层模型不同的是，CI&CD 是一种类似御尾蛇的结构。

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/CI%26CD1.png)

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/CI%26CD3.png)

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/CI%26CD4.png)

## 组成

CI&CD 流水线上的步骤相对灵活，个人认为，总的来说有以下几个是必须的：

- PLAN
- CODE
- BUILD
- TEST
- DEPLOY STAGING
- REVIEW
- ACCEPTANCE TEST
- DEPLOY PRODUCTION
- MONITOR

## PREPARE PIPELINE

PLAN --> CODE 属于 PREPARE PIPELINE。需求如何扎实地交付给开发？需求文档要不要写，要写的话如何写？如何让需求文档和代码实现之间可以比较好地映射起来？这些都是这一层要思考的，这一层却很容易被弱化甚至忽略，轻 PLAN 重 CODE 往往会导致代码容易出现 bug，试想 PLAN 已经有漏洞了，实现出来的 CODE 肯定也会有问题的。

## CI PIPELINE

BUILD --> TEST --> DEPLOY STAGING 属于 CI PIPELINE
