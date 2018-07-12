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

对于第一点，通过 [RFC 2616 对 GET 的描述](https://tools.ietf.org/html/rfc2616#section-9.3) 和 [RFC 2616 对 POST 的描述](https://tools.ietf.org/html/rfc2616#section-9.5) 可以知道，标准中并没有明确指出 GET 的传参只能用 URL，POST 的传参只能用 BODY。

先来看 GET。标准只是强调了 GET 的语义是检索/查询，而且可以是 “有条件的查询” 或 “局部查询”，两者的作用都是为了减少不必要的 HTTP 请求和传输量。同时，
`See section 15.1.3 for security considerations when used for forms.` 这句其实也说明了 GET 是可以以 form 的形式传参的。

再来看 POST。虽然 `POST is designed to allow a uniform method to cover the following functions: - Providing a block of data, such as the result of submitting a form, to a data-handling process;` 这句指出了 POST 的其中一个功能是提交 form，但是全部看下来，也没说不能用 URL 传参。


