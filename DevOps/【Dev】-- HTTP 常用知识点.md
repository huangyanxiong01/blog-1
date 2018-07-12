- GET POST 误解
- 缓存：If-None-Match: ETag & Cache-Control: max-age/no-cache/public/private
- 压缩：gzip
- 跨域请求
- 状态码

# GET 和 POST 的误解

对于两者的区别，普遍的答案如下：

- GET 只能用 URL 传参，而 POST 只能用 BODY 传参
- GET 的 URL 会有长度上的限制，而 POST 的数据则可以非常大
- GET 没 POST 安全，因为数据在地址栏上可见

对于第一点，通过 [RFC 2616 对 GET 的描述](https://tools.ietf.org/html/rfc2616#section-9.3) 和 [RFC 2616 对 POST 的描述](https://tools.ietf.org/html/rfc2616#section-9.5) 可以知道，标准中并没有明确指出 GET 的传参只能用 URL，POST 的传参只能用 BODY 这个观点。

先来看 GET。标准只是强调了 GET 的语义是检索/查询，而且可以是 “有条件的查询” 或 “局部查询”，两者的作用都是为了减少不必要的 HTTP 请求和传输量。同时，
`See section 15.1.3 for security considerations when used for forms.` 这句其实也说明了 GET 是可以以 form 的形式传参的。

再来看 POST。虽然 `POST is designed to allow a uniform method to cover the following functions: - Providing a block of data, such as the result of submitting a form, to a data-handling process;` 这句指出了 POST 的其中一个功能是提交 form，但是全部看下来，也没说不能用 URL 传参。

个人认为，这种观点是因为 HTML 对 HTTP 的使用标准导致的。扯一下，HTTP 协议是一个应用层的标准，相比 TCP/IP 这种底层的数据传输协议就没那么严格了，退一步来说，即使应用层协议不符合标准，它也只是以数据的身份被 TCP/IP 封装，还是能够被传输出去的，只是到了应用层解析可能会出错而已，这就不像 TCP/IP 如果不符合标准连传都传不出去。因此第一点并不是正确的。

对于第二点，同样通过上述的 RFC 2616 标准中的描述可以知道，并没有对数据量作出要求。个人认为，这种观点源自于实际需求，数据量太大无论对于网络传输还是两端的程序来说都不是好事情，因此在实际的实现上对数据量的要求出现了一些标准。因此第二点是错误的。

对于第三点，GET, POST 是请求方法，跟安全没有直接的关系。即使是 POST，在 HTTP 下也能通过抓包看到传输的数据是什么，只是没有在 URL 上面那么明显罢了。因此第三点是错误的。
，
# 缓存

缓存的好处不言而喻，通过减少甚至无需发起 HTTP 请求来提升服务的性能和用户的体验。虽然缓存随着 HTTP 的演进也一直在改变，但是，个人认为，有三个缓存相关的 HTTP Header 是必须要掌握的：If-None-Match, ETag, Cache-Control。因为这三个 HTTP Header 已经可以满足缓存需求，同时当今主流的浏览器都支持这三个头。需要明确的是，这里的缓存指的是客户端，或者是代理服务器上的缓存，不包括终端服务器、Redis 等。

- ETag：服务器的响应头，代表资源的标识，可以是资源的 hash 值，当资源发生更新时，对应的 ETag 也会改变。当服务端允许缓存时，会在第一次请求的响应中带着 ETag 返回给客户端
- If-None-Match：客户端的请求头，配合 ETag 使用 (`If-None-Match: ETag`)。当客户端将 `If-None-Match: ETag` 发送到服务器时，服务器会先判断服务器上资源的 ETag 有没有变化，如果没有则返回状态码 304，否则返回更新后的资源和新的 ETag
- Cache-Control：服务器的响应头，代表缓存策略
  - 代表缓存作用域
    - public：默认值，代表客户端和代理都可以缓存这些信息
    - private：代表只有客户端可以缓存
  - 代表缓存方式
    - max-age：只要缓存在有效期内，客户端无需发起 HTTP，直接使用本地缓存副本即可
    - no-cache：即使缓存在有效期内，客户端也需要发起 HTTP 实时确保缓存真的没有过期
    - no-store：不准客户端和代理进行缓存

max-age 策略下的 HTTP 缓存的基本交互图如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/HTTP缓存.png)

HTTP 缓存策略决策图如下：

![](https://raw.githubusercontent.com/hsxhr-10/picture/master/HTTP缓存1.png)

# 跨域

跨域分广义和狭义两种。










