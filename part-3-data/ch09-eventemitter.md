# 第 9 章 EventEmitter：事件驱动的字面实现

> **本章问题**：Node.js 号称"事件驱动"，那 `emit()` 一个事件时到底发生了什么？是异步派发？消息队列？还是……比想象中简单得多的东西？

## 9.1 意料之外的答案

先做实验：

```js
const { EventEmitter } = require('events');
const ee = new EventEmitter();

ee.on('ping', () => console.log('B: 监听器执行'));

console.log('A: emit 之前');
ee.emit('ping');
console.log('C: emit 之后');
// 输出：A → B → C
```

如果 emit 是异步的，输出应该是 A → C → B。但事实是 A → B → C——**监听器在 emit 的调用栈里同步执行完毕，emit 返回时一切已经结束**。

EventEmitter 的核心简化到伪代码只有几行：

```js
// 本质示意（省略边界处理）
class EventEmitter {
  #listeners = {};                    // { 事件名: [函数数组] }
  on(name, fn)  { (this.#listeners[name] ??= []).push(fn); }
  emit(name, ...args) {
    for (const fn of this.#listeners[name] ?? []) fn(...args);  // 同步 for 循环！
  }
}
```

没有队列，没有调度，没有线程——**一个存回调的字典，加一个同步 for 循环**。这就是"事件驱动"的字面实现。

那"异步"从哪来？从**谁在什么时候调用 emit**。第 4 章的链路现在可以补全最后一环：

```
内核发现 fd 就绪 → epoll_wait 返回 → libuv 调 C++ 回调
  → MakeCallback 进入 JS → JS 内部代码调用 socket.emit('data', buf)
                                        ▲
                    异步性来自这里（事件循环决定何时触发）
                    emit 本身只是同步分发（for 循环调用监听器）
```

**异步的是"事件何时发生"，同步的是"事件如何分发"。** 分不清这两层，就会误判执行顺序、误解性能问题。

## 9.2 同步分发的推论

推论一：**监听器阻塞 = 全体阻塞**。emit 的 for 循环里某个监听器耗时 100ms，后面的监听器、emit 的调用方、乃至整个事件循环（第 4 章）都等着这 100ms。

推论二：**监听器按注册顺序执行**，且 emit 返回后所有监听器保证已执行完——可以依赖这个顺序做逻辑。

推论三：**事件没人听，就当没发生**。emit 返回布尔值告诉你"有没有人听到"。错过了就是错过了，EventEmitter 不存历史消息——它是喇叭，不是信箱。（唯一的例外，是下一节的 'error'。）

常用 API 一览：

| 方法 | 语义 |
|------|------|
| `on(name, fn)` / `off(name, fn)` | 订阅 / 退订 |
| `once(name, fn)` | 只触发一次，自动退订 |
| `emit(name, ...args)` | 同步分发，返回"是否有监听器" |
| `events.once(ee, name)` | Promise 化的一次性等待（配合 await） |

## 9.3 'error'：唯一的特殊事件

EventEmitter 对 `'error'` 有一条独有的硬规则：

```
emit('error', err) 时：
  有监听器  → 正常同步分发，跟别的事件一样
  没监听器  → 直接 throw err
              → 没有 try/catch 接住 → 进程崩溃退出
```

一个真实的事故模式：服务运行数月，某晚对端网络抖动，一个平时不出错的 socket 发出 `'error'`——没人监听——进程消失。日志里只有一行 `Unhandled 'error' event`。

为什么这样设计？因为 I/O 错误发生在异步回调里，普通 try/catch 根本包不住（栈早就切换了）。如果 EventEmitter 默默吞掉没人听的 error，错误就**彻底消失**——连接悄悄坏死、数据悄悄丢失，比崩溃可怕得多。Node.js 选择了**快速失败**：要么你显式处理，要么进程死给你看。

工程铁律由此而来：**每个 socket、每个 stream、每个长期存活的 EventEmitter，必须挂 'error' 监听**。第 8 章推荐 pipeline 的原因之一，正是它替流水线上每个流接管了错误。至于 `process.on('uncaughtException')`——它是记录现场、优雅退出用的最后底线，不是"继续运行"的免死金牌（进程状态已不可信）。

## 9.4 谁在继承 EventEmitter

第 8 章说 Stream 继承 EventEmitter，其实继承者遍布整个运行时：

```
EventEmitter
  ├── Stream 家族（Readable/Writable/...）    'data' 'end' 'drain' 'error'
  ├── net.Server / net.Socket                'connection' 'data' 'close'
  ├── http.Server（继承 net.Server）          'request' 'upgrade'
  ├── ChildProcess                           'exit' 'message'
  ├── Worker（worker_threads）                'message' 'exit'
  └── process 对象本身                        'beforeExit' 'SIGINT' 'uncaughtException'
```

为什么大家都继承它？因为它恰好是**回调世界的组织范式**：I/O 对象的一生会发生多种、多次、不定时的事情（连上了、来数据了、出错了、关闭了），"为每类事情注册任意多个处理函数"正是 EventEmitter 提供的最小完备接口。它是 Node.js 编程模型的地基，比 Stream 更底层。

## 9.5 遗留问题：事件把"来龙去脉"弄丢了

同步分发有个隐蔽的副作用。看一个 Web 服务的常见困境：

```js
server.on('request', (req, res) => {
  // 这里知道请求 ID 是 42
  db.query(sql, (err, rows) => {
    // 这个回调由 db 连接的 emit 触发
    // ——它怎么知道自己属于请求 42？
    log('查询完成');   // 想在日志里带上请求 ID，带不上
  });
});
```

回调被 emit 调用时，调用栈属于"数据到达"这个事件，**不属于任何请求**。跨越异步边界后，"我在为谁工作"这条信息断了。

Node.js 为此提供了两层机制：

- **asyncId 因果链**：每个异步资源（第 3 章 AsyncWrap 的那个"身份证"）记着自己的 id 和"是谁创建了我"（triggerAsyncId），串成完整的异步族谱，`async_hooks` 可以观测它——这是诊断工具的地基；
- **AsyncLocalStorage**：应用层的解法。`als.run(store, fn)` 之后，fn 引发的**整条异步调用链**里，任何位置调用 `als.getStore()` 都能拿回 store：

```js
const als = new AsyncLocalStorage();

server.on('request', (req, res) => {
  als.run({ reqId: nextId() }, () => handle(req, res));
});

// 任意深度的异步回调里：
function log(msg) {
  console.log(`[req ${als.getStore()?.reqId}] ${msg}`);   // 拿到 42 了
}
```

现代实现依托 V8 的原生上下文延续机制（AsyncContextFrame），开销已低到可默认用于生产。全链路日志、分布式追踪（trace id 透传）都建立在它上面。

这里只给出结论性的全貌。这套机制凭什么成立？它能不能进一步穿过第 14 章的线程与进程边界，把不同执行现场串回同一条主线？——完整推导留给第五部收尾的第 15 章。

## 9.6 本质小结

> **一句话本质**：emit 是一个同步 for 循环——异步性来自事件循环决定"何时 emit"，而非 emit 本身；理解这一点，加上"error 没人听就崩溃"的铁律，就理解了 Node.js 事件模型的全部脾气。

要点：

1. **EventEmitter = 回调字典 + 同步 for 循环**——无队列无调度；emit 返回时监听器已全部执行完。
2. **异步在"何时触发"，同步在"如何分发"**——两层分清，执行顺序不再神秘。
3. **'error' 无监听即 throw、即崩溃**——快速失败设计；长期存活的 emitter 必挂 error 监听。
4. **事件是喇叭不是信箱**——不存历史，emit 时没人听就永远错过（once/queueing 需自建）。
5. **异步边界会弄丢上下文**——asyncId 链是观测地基，AsyncLocalStorage 是应用层标准解法。

## 下一章引子

到这里，前三部的零件全部到齐：V8 执行、Binding 破壁、事件循环心跳、双路 I/O、fd 通道、Buffer 载体、Stream 流动、EventEmitter 分发。

零件各自讲透了，但在去看"谁把它们装配成机器"之前，先看一场合练——Node.js 的成名之作，正是这些零件搭出的第一个完整应用：**HTTP 服务**。你每天在写的 `http.createServer`，底下调动的正是前面九章的每一样东西，一样不多，一样不少。

下一章：HTTP——七个机制的第一次合练。

---

[← 上一章：Stream](./ch08-stream.md) | [下一章：HTTP →](../part-4-http/ch10-http.md)
