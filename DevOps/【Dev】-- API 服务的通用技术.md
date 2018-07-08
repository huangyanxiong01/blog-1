# 导引

从一开始的网站到 APP，再到之前火起来的微信公众号、小程序等，产品的呈现方式一直有新的花样。但是，对于后端开发来说，开发所需的技术点大体上还是没有大变化的，最终都是以 API 服务的形式呈现给对端。

这里将抛开具体的开发语言，重点抽象出基于 HTTP/HTTPS 协议的 API 服务的通用技术点，并稍作讨论。注意，个人认为，虽然构建 API 服务的很多技术点都有与之相对应的标准，但是，在实际的开发中，往往会发现生搬硬套标准反而低效，类似的场景还有 CI/CD 的那些标准。因此，下面讨论的只是我在实际开发的过程中认为不错的点，都是个人经验之谈，不是标准概念，不是标准概念，不是标准概念。

# 方法

## API 架构风格

目前主流的有 RESTful 和 RPC/REST-RPC 两种方式，以前貌似还有个 SOA。

RESTful 以资源为核心，能充分利用 HTTP 协议原生的请求方法 (GET, POST, PUT, DELETE 等)，而无需在 API 的 URL 加上额外的动词，并且同一条 URL 加上不同的请求方法后也代表不同的意思。比如为文章这个资源来设计 API，那么最基础的几个 API URL 如下：

- GET /articles：查询文章列表
- GET /articles/id：查询文章详情
- POST /articles/：创建文章
- PUT /articles/id：修改文章
- DELETE /articles/id：删除文章

RPC 以操作为核心，只会用到 HTTP 协议中的 GET 和 POST 方法，会在 API 的 URL 加上明确的动词。同样以文章这个资源为例，那么 RPC 对应的最基础的几个 API URL 如下：

- GET/POST /get_article_list：查询文章列表
- GET/POST /get_article_detail：查询文章详情
- GET/POST /create_article：创建文章
- GET/POST /modify_article：修改文章
- GET/POST /delete_article：删除文章

总的来说，两者的核心关注点不同，RESTful 关注的是 API 操作的资源是什么，并且能跟 HTTP 方法无缝融合。而 RPC 更关注 API 的操作是什么，并且要能在 URL 上明确体现出来。这里忍不住要吐槽网上有一些关于这两种风格撕逼或者一味鼓吹某一种风格的言论，其实讲真，只要团队接受，并且有能力落地，爱用哪种用哪种，Swagger 也不会因为你是 RPC 风格就不让你使用它来搭建 API 文档服务。

