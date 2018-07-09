# 导引

从一开始的网站到 APP，再到之前火起来的微信公众号、小程序等，产品的呈现方式一直有新的花样。但是，对于后端开发来说，开发所需的技术点大体上还是没有大变化的，最终都是以 API 服务的形式呈现给对端。

这里将抛开具体的开发语言，重点抽象出基于 HTTP/HTTPS 协议的 API 服务的通用技术点，并稍作讨论。注意，个人认为，虽然构建 API 服务的很多技术点都有与之相对应的标准，但是，在实际的开发中，往往会发现生搬硬套标准反而低效，类似的场景还有 CI/CD 的那些标准。因此，下面讨论的只是我在实际开发的过程中认为不错的点，都是个人经验之谈，不是标准概念，不是标准概念，不是标准概念。

# 方法

## 风格

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

## 协议

尽量用 HTTPS，全站 HTTPS 当然最好了，如果做不到全站，那么至少也要在一些敏感、安全要求高的地方用，比如跟密码相关的 API。

退一步来说，如果只能用 HTTP，那么就一定要做签名了，因为不做签名相当于裸奔，随便一抓包就能修改请求。具体的做法如下：

1. 客户端缓存着一个用于签名的变量 `secret`，服务端也有对应的 `secret`，并且和每个用户的唯一标记关联起来，比如 `id`
2. 客户端在发起请求之前，用 md5 之类的散列函数，为请求参数、`id`、`secret`、时间戳 (可选，用作验证签名的有效期) 生成一个唯一的字符串 `signature`
3. 客户端将请求参数、`id`、`signature`、时间戳，一块发送到服务端。当然 `secret` 不要发送，这样即使被抓包截获了，没有 `secret` 也就不能仿造签名了，也就不篡改参数了
4. 服务端对参数进行再次签名验证，一致的才返回数据，不一致可以直接 403

下面是 Python 实现的一个签名装饰器：

```
def resource_protected():
    """
    API签名装饰器
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 用timestamp防止重放攻击, 签名的有效期是10分钟(注意，前端传过来的是utc，即少8个小时的)
            if ((arrow.utcnow().timestamp -
                 arrow.get(kwargs['timestamp']).timestamp) / 60) > 10:
                raise tornado.web.HTTPError(403)
            
            # 服务端再次签名所需的参数
            id = kwargs['id']
            signature = kwargs['signature']

            secret = RK.get_hash_value(Setting.REDIS_SECRET_STORE, id)
            if not secret:
                secret = repair_secret(secret, id)
            # 再次签名
            server_signature = make_signature(secret, **kwargs)
            
            # 验证服务端的签名和客户端的是否一致
            if server_signature == signature:
                return func(*args, **kwargs)
            else:
                raise tornado.web.HTTPError(403)

            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## 版本

有两种做法，一种是现实在 API 的 URL 上，如 `domian.com/api/v1/xxx/`。另一种是随着响应的数据返回，如 `{'code': 200, 'resp': {'version': 'v1', 'data': []}}`。个人认为如果是作为第三方 API 给别人使用的，第一种会更直观，如果是内部使用的话，团队接受就行。

## 无状态























