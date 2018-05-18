# <font color=#42b983>#</font> 目录
```
.
├── WSGI 协议简介
|   ├── 是什么
|   ├── 为什么
|   └── 怎么做
├── wsgiref 及其依赖关系
|   ├── wsgiref 目录结构
|   └── 依赖关系
|       ├── 从目录结构层面分析
|       └── 从类层面分析
├── 一次 HTTP 请求之旅
└── 结语
```

# <font color=#42b983>#</font> WSGI 协议简介

### 是什么

较权威的解释可以参考 [wikipedia](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) 或 [PEP 3333](https://www.python.org/dev/peps/pep-3333/)。 直白点说， WSGI 协议的实现包括两个主要组成部分：服务端和应用端。

服务端就是平时所说的应用服务器，常见实现有：
- uWSGI
- gunicorn
- Tornado 的服务器部分
- 一般 web 框架都会自带的测试服务器

应用端就是平时所说的 web 框架，常见实现有：
- flask
- bottle
- Tornado 的 web 框架部分

### 为什么

WSGI 协议可以解耦服务端和应用端，只要是遵守 WSGI 协议所实现的服务端和应用端，都可以进行两两组合，从而达到软件复用的效果。可类比 HTTP 协议解耦服务器和浏览器。

### 怎么做

下面就以 Python 标准库中 wsgiref 的实现来窥探一下 WSGI 协议的一种实现方式。下文中所讨论的源码为 [Python version 3.8.0 alpha 0](https://github.com/zongzhenh/cpython/tree/master/Lib)

# <font color=#42b983>#</font> wsgiref 及其依赖关系

### wsgiref 目录结构

```
wsgiref
├── __init__.py         # 包简介
├── handlers.py         # 包含实现 WSGI 协议服务端/网关端的基础类
├── headers.py          # 管理 HTTP 响应头
├── simple_server.py    # 实现了 WSGI 协议的服务端和一个简单的用于测试的应用端
├── util.py             # 各种常用的工具函数
└── validate.py         # 各种验证/断言函数
```

> 小结：
>
> - 核心部分为 handlers.py 和 simple_server.py
> - wsgiref 主要还依赖 cpython/Lib/http/server.py 和 cpython/Lib/socketserver.py 两个模块。通过下面对依赖关系的分析，会更清楚各模块之间的关系和各自的作用

### 依赖关系

#### 从目录结构层面分析

![图1](https://user-gold-cdn.xitu.io/2018/4/8/162a4cd92632a5e4?w=770&h=1056&f=png&s=113873)

> 小结：wsgiref 涉及的包和模块如上图所示

#### 从类层面分析

> 注意，下图只标注出核心的类和方法

![图2](https://user-gold-cdn.xitu.io/2018/4/8/162a5bb2e7c58750?w=2504&h=1276&f=png&s=1316148)
![图3](https://user-gold-cdn.xitu.io/2018/4/8/162a5babdcce02e2?w=2384&h=660&f=png&s=681946)

> 补充，看到 BaseServer 的类图，在初始化 RequestHandlerClass 时，会以 socket 连接作为参数传递给构造函数。对应源码位置为：cpython/Lib/wsgiref/socketserver.py 357 行

> 小结：wsgiref 涉及的核心类可归纳成三大类
>
> - XXXServer
>   - 循环非阻塞地监听请求（经典的服务器端编程模型）
>   - 以就绪的 socket 连接为参数，初始化获取到的 XXXRequestHandler 对象
>
> - XXXRequestHandler
>   - 将 XXXServer 传递过来的 socket 连接封装成对应的文件对象
>   - 复写 handle 方法，在该方法中，以封装好的文件对象为参数，传递给 XXXHandler 的构造函数，并初始化 XXXHandler 对象，XXXHandler 对象执行 run 方法
>   - 以自身（类）为参数，传递给 XXXServer 的构造函数
>
> - XXXHandler
>   - 复写 _write 方法
>   - 复写 _flush 方法
>   - 执行 run 方法，在该方法中，调用 application 对象（应用端/web 框架），application 对象根据 routing 规则, 找到请求 url 对应的处理函数，得到处理结果。最后将处理结果，利用封装好的 socket 对象发送结果到客户端

## <font color=#42b983>#</font> 一次 HTTP 请求之旅

> 注意：
>
> * 本次  HTTP 之旅会适度地简化，重点分析正常流程所涉及的核心语句，一些如异常处理的情况则暂时先跳过，后续可以出个外传继续聊...
>
> * 考虑到大家看了上面的 `从类层面分析` 之后，应该会处于似懂非懂的状态，因此下面的分析会复用部分 `从类层面分析` 小结中的语句，方便大家对照着看，从而更好地理解

<font color=#e96900>*</font> 启动 WSGI 服务端

```
with make_server('', 8000, demo_app) as httpd:
    httpd.serve_forever()
```

<font color=#e96900>*</font> 客户端发起 HTTP 请求

<font color=#e96900>*</font> 监听请求

> 进入到 def serve_forever(self, poll_interval=0.5) 方法

```
with _ServerSelector() as selector:
    selector.register(self, selectors.EVENT_READ)

    while not self.__shutdown_request:
        ready = selector.select(poll_interval)
        if ready:
            self._handle_request_noblock()
```

- selector 为标准库 select（I/O 多路复用） 的进一步封装
- selector.register(self, selectors.EVENT_READ) 注册读事件
- ready = selector.select(poll_interval) 事件循环，当有就绪事件则返回
- self._handle_request_noblock() 处理请求

> 源码位置：cpython/Lib/wsgiref/socketserver.py 228-234 行

<font color=#e96900>*</font> 处理请求-1

> 接上，进入到 self._handle_request_noblock()

```
try:
    request, client_address = self.get_request()
except OSError:
    return
if self.verify_request(request, client_address):
    try:
        self.process_request(request, client_address)
```

- request, client_address = self.get_request() 根据 self.get_request 方法的实现可知，该语句等价于 connection, address = socket.accept()，也就是说，是在这里获取了 socket 连接
- self.process_request(request, client_address) 处理请求

> 源码位置：cpython/Lib/wsgiref/socketserver.py 307-313 行

<font color=#e96900>*</font> 处理请求-2

> 接上，进入到 self.process_request(request, client_address)

```
self.finish_request(request, client_address)
self.shutdown_request(request)
```

- self.finish_request(request, client_address) 以就绪的 socket 连接为参数，初始化获取到的 XXXRequestHandler 对象
- self.shutdown_request(request) 关闭连接

> 源码位置：cpython/Lib/wsgiref/socketserver.py 344-345 行

<font color=#e96900>*</font> 初始化 XXXRequestHandler 对象

> 接上，进入 self.finish_request(request, client_address)

```
self.RequestHandlerClass(request, client_address, self)
```

- self.RequestHandlerClass(request, client_address, self) 以就绪的 socket 连接为参数，初始化获取到的 XXXRequestHandler 对象

> 源码位置：cpython/Lib/wsgiref/socketserver.py 357 行

<font color=#e96900>*</font> 执行 setup 方法和 handle 方法

> 接上，进入 XXXRequestHandler 构造函数

```
def __init__(self, request, client_address, server):
    self.request = request
    self.client_address = client_address
    self.server = server
    self.setup()
    try:
        self.handle()
    finally:
        self.finish()
```

```
def setup(self):
    self.connection = self.request
    if self.timeout is not None:
        self.connection.settimeout(self.timeout)
    if self.disable_nagle_algorithm:
        self.connection.setsockopt(socket.IPPROTO_TCP,
                                   socket.TCP_NODELAY, True)
    self.rfile = self.connection.makefile('rb', self.rbufsize)
    if self.wbufsize == 0:
        self.wfile = _SocketWriter(self.connection)
    else:
        self.wfile = self.connection.makefile('wb', self.wbufsize)
```

- self.setup() 将 XXXServer 传递过来的 socket 连接封装成对应的文件对象

- self.handle() 执行子类复写的 handle 方法，在该方法中，以封装好的文件对象为参数，传递给 XXXHandler 的构造函数，并初始化 XXXHandler 对象，XXXHandler 对象执行 run 方法

> 源码位置：cpython/Lib/wsgiref/socketserver.py 710 行，712 行，755-766 行

<font color=#e96900>*</font> 初始化 XXXHandler 对象

> 接上，进入 handle 方法。因为 handle 方法都是在子类中被复写的，所以，这里以 cpython/Lib/wsgiref/simple_server.py 的 WSGIRequestHandler 类为例

```
handler = ServerHandler(
    self.rfile, self.wfile, self.get_stderr(), self.get_environ()
)
handler.request_handler = self      # backpointer for logging
handler.run(self.server.get_app())
```

- handler = ServerHandler(
    self.rfile, self.wfile, self.get_stderr(), self.get_environ()
) 以封装好的文件对象为参数，传递给 XXXHandler 的构造函数，并初始化 XXXHandler 对象
- handler.run(self.server.get_app()) XXXHandler 对象执行 run 方法

> 源码位置：cpython/Lib/wsgiref/simple_server.py 129-133 行

<font color=#e96900>*</font> 执行 run 方法

> 接上，进入 run 方法

```
self.setup_environ()
self.result = application(self.environ, self.start_response)
self.finish_response()
```
- self.setup_environ() 设置 environ 字典
- 调用 application 对象（应用端/web 框架），application 对象根据 routing 规则, 找到请求 url 对应的处理函数，得到处理结果
- self.finish_response() 利用封装好的 socket 对象发送结果到客户端

> 源码位置：cpython/Lib/wsgiref/handlers.py 136-138 行

## <font color=#42b983>#</font> 结语

本文首先简单介绍了 WSGI 协议，然后以 wsgiref 的源码实现为着手点，重点分析了该实现中各个类的依赖关系和各自起到的作用，最后以一次 HTTP 请求的接收到发送全过程作为路线图, 再次串联起各个关键的类和流程。

> 附：[wsgiref 行级源码注释](https://github.com/zongzhenh/_backup/tree/master/wsgiref)

转载请标明原文出处
