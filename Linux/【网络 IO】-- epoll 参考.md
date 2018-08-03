# 按顺序

1. https://cdn2.jianshu.io/p/548ef6a267ba
2. http://wangzhilong.github.io/2015/09/30/epoll/
3. http://www.valleytalk.org/2012/08/05/epoll-linux%E5%86%85%E6%A0%B8%E6%BA%90%E4%BB%A3%E7%A0%81%E5%AE%9E%E7%8E%B0%E5%8E%9F%E7%90%86%E5%88%86%E6%9E%90/
4. https://github.com/torvalds/linux/blob/master/fs/eventpoll.c
5. http://blog.chinaunix.net/uid-20687780-id-2105157.html
6. http://scotdoyle.com/python-epoll-howto.html

# 

- 可监控的 fd 理论上无限制 (具体看物理内存 hold 不 hold 得住)
- 每次检查是否有就绪的 fd 时，无需将所有的 fd 从 user space copy 到 kernel space，只需调用 `epoll_ctl` 增量式地添加 fd (即往 `struct eventpoll` 所维护的 red black tree 中插入封装后的 fd --- `struct epitem`)
- 每次检查是否有就绪 fd 时，无需遍历所有的 fd，只需遍历就绪链表 rdllink
