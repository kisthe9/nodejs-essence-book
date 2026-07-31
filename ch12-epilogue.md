# 第 12 章 万物归一：一个请求的一生

> **本章问题**：不再有新问题。这一章兑现前言的承诺——把十一章的机制放进同一部电影，逐帧播放一个 HTTP 请求从网卡到回调再回到网卡的全过程。

## 12.1 开机（发生在一切之前）

```bash
node server.js
```

**［第 10 章］** 进程初始化 → 三层容器落成（Isolate/Environment/Realm，**第 9 章**）→ 快照恢复引导堆，process 就位 → 加载 server.js：

```js
// server.js
const http = require('http');
http.createServer((req, res) => {
  fs.readFile('./greeting.txt', (err, data) => {
    res.end(data);
  });
}).listen(8080);
```

**［第 2 章］** `require('http')`：CJS 加载器逐级解析，http.js → net.js，最终 `internalBinding('tcp_wrap')` 穿门，`new TCP()` 在 C++ 侧诞生 TCPWrap，与 JS 的 Server 对象通过内部字段互相锁定。

**［第 5 章］** `listen(8080)`：一路下行到系统调用，内核创建监听 socket——一个 inode、一个 fd。**［第 4 章］** 这个 listen-fd 被注册进 epoll。**［第 3 章］** 事件循环启动，poll 阶段抵达 `epoll_wait`，阻塞——

进程睡着了。CPU 占用 0%。一个活跃句柄（listen-fd）让它不退出（**第 10 章**）。

## 12.2 第一帧：连接到达

某个浏览器发起 TCP 握手。内核协议栈完成三次握手，把新连接放进监听 socket 的队列，**listen-fd 变为可读**。

**［第 3、4 章］** `epoll_wait` 醒来，返回就绪列表。libuv 顺着事件里存的指针直接找到 TCPWrap，调用其连接回调：`accept()` 取出新连接——内核分配 **conn-fd**（**第 5 章**：新的 struct file，指向这条连接的 socket inode）。conn-fd 被设为非阻塞、注册进 epoll。

**［第 2 章］** MakeCallback 拉起 JS。**［第 8 章］** `server.emit('connection', socket)`——一个同步 for 循环执行监听器，http 模块在其中给 socket 挂上数据解析器。

## 12.3 第二帧：请求数据到达

浏览器发出 `GET / HTTP/1.1 ...`。字节流经网卡进入内核，堆进 conn-fd 的接收缓冲区，**conn-fd 可读**。

**［第 4 章］** epoll_wait 再次返回。libuv 循环 `read()` 直到 EAGAIN——**［第 6 章］** 每次 read 的目的地是一个 Buffer：C++ 拿着 BackingStore 的裸指针递给系统调用，内核字节直接落进 JS 可见的内存，零拷贝。

**［第 8 章］** `socket.emit('data', buf)` 同步分发。HTTP 解析器逐字节解析出方法、路径、头部，凑齐后：`server.emit('request', req, res)`——**你的回调终于登场**。此刻距离 epoll_wait 醒来，一微秒级的同步链，全程无一次线程切换。

## 12.4 第三帧：文件 I/O 的岔路

你的回调调用 `fs.readFile('./greeting.txt', cb)`。

**［第 4 章］** 磁盘文件不进 epoll——任务被投进线程池。**主线程立刻返回**，继续转事件循环，去服务其他连接（这就是"这段时间它还接了另外 300 个请求"的原因）。

工人线程 `open()` → `read()`（老老实实阻塞在磁盘上）→ 数据进 Buffer → `close()`。完工，向内部管道写一字节唤醒 epoll_wait。

**［第 3 章］** 事件循环在下一圈把完成事件派回：**［第 2 章］** MakeCallback → 你的 `cb(null, data)` 执行。**［第 8 章］** 若你用的是 AsyncLocalStorage，此刻 getStore() 依然能拿到本请求的上下文——异步族谱没有断。

## 12.5 第四帧：响应离场

`res.end(data)`：http 模块拼好响应头，与 body 一起送进 socket 的 Writable 侧。

**［第 7 章］** 若 data 很大或对端很慢：write 返回 false，上游暂停；内核发送缓冲满后 TCP 窗口收缩，压力传到浏览器侧——背压全链启动，服务器内存稳如泰山。

**［第 5 章］** 最终每个 chunk 经 `write(conn-fd)` 交给内核——与写文件是同一个系统调用，f_op 多态分发到协议栈。字节上网卡，离场。

keep-alive 连接回到 epoll 继续待命；连接关闭时，close 回调在 **第 3 章** 的 close 阶段执行，conn-fd 归还，fd 表腾出一个号码牌（**第 5 章**：忘了这步的积累就是 EMFILE）。

## 12.6 全片回放

```
 启动    [10]装配线 → [9]三层容器 → [2]require+穿门 → [5]listen-fd → [3]循环入睡
                                                                      │
 连接    内核握手 → [3/4]epoll 醒 → accept 得 conn-fd[5] → [8]emit('connection')
                                                                      │
 请求    字节进内核缓冲 → [4]循环read至EAGAIN → [6]零拷贝入Buffer → [8]emit('request')
                                                                      │
 处理    [4]readFile 走线程池，主线程继续接客 → 完工唤醒 → [2]MakeCallback → 你的cb
                                                                      │
 响应    res.end → [7]背压控流 → [5]write(conn-fd) 多态分发 → 网卡 → 浏览器
                                                                      │
 退场    SIGTERM → [10]server.close 撤句柄 → 循环自然停 → 善终
（多核： [11]以上全部 × N 份容器，cluster 分发连接）
```

十一章，一个请求，一张图。如果每一帧你都能自己讲出"为什么"，这本书的任务完成了。

## 12.7 可以带走的东西

合上书之前，把 Node.js 教给我们的普适设计原则带走——它们不只属于 Node：

1. **把约束当公理，而不是当敌人。** Node 没有对抗单线程，而是从它推导出整套架构。好架构不是没有约束，而是与约束共生。
2. **统一抽象是杠杆。** 内核用 fd 统一万物，Node 用 Stream 统一 fd，用 EventEmitter 统一回调——每一层统一都让上层的复杂度坍缩一个量级。
3. **把等待外包，把执行留下。**（事件循环）识别系统里"等"与"做"的边界，是所有高并发设计的第一步。
4. **反馈回路优于无限缓冲。**（背压）任何生产者-消费者系统，没有反向的减速信号，缓冲区就是定时炸弹。
5. **失败要响，不要哑。**（error 铁律）静默吞掉的错误比崩溃贵一百倍。
6. **复制比共享便宜——当协调成本高于复制成本时。**（Worker/Cluster）分布式系统的古老智慧，在单机上同样成立。
7. **给自己留一条不可信任的假设。**（primordials）平台不信任应用，内核不信任用户态——防御性边界是健壮系统的标配。

## 12.8 终点即起点

本书刻意收窄在"本质"层：七个机制、一条因果链。往外走的方向：

- **读源码**：现在你有了地图——`lib/` 是门内的 JS，`src/` 是门后的 C++，`deps/uv` 是心脏，`deps/v8` 是隔离舱。从 `lib/net.js` 顺着一个 listen 调用往下追一次，胜过十篇文章。
- **上层子系统**：HTTP/2、TLS、crypto、WASI——全是这七个机制的组合应用，附录给了映射表。
- **横向对比**：拿本书的框架去审视 Go（协程把"等待"藏进运行时）、Rust/tokio（所有权与异步的另一种答案）——对比之处，正是设计取舍显形之处。

感谢你读到这里。愿你下次面对"进程为什么不退出""内存为什么涨"这类问题时，脑中浮现的不是搜索框，而是那条因果链。

---

[← 上一章：多核之路](./part-4-container/ch11-multicore.md) | [附录 →](./appendix.md) | [返回目录](./README.md)
