- GET POST 区别
- 缓存：If-None-Match: ETag & Cache-Control: max-age/no-cache/public/private
- 压缩：gzip
- 跨域请求
- 状态码

# GET 和 POST 的区别

对于两者的区别，普遍的答案如下：

- GET 使用 URL 传参，而 POST 将数据放在 BODY 中
- GET 的 URL 会有长度上的限制，而 POST 的数据则可以非常大
- GET 没 POST 安全，因为数据在地址栏上可见

对于第一点，我们截取 [RFC 2616 中 GET 的描述](https://tools.ietf.org/html/rfc2616#section-9.3)
