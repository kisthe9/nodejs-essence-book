# 第 12 章 异步上下文：穿越边界的因果链

> **本章问题**：第 8 章留下过一个困境——回调跨越异步边界后，"我在为谁工作"这条信息就断了。第 11 章又立起一道道容器边界：线程、进程，层层隔离。有没有一种机制，能让一条"因果链"穿过所有异步回调、甚至穿过线程与进程的边界，把散落各处的执行现场串回同一条主线？

## 12.1 断裂的调用栈

先看清问题为什么难。同步世界里不需要任何额外机制：

```
handle(req42)
  └── checkAuth()          ← 沿调用栈向上回溯，就知道"我在为 req42 工作"
        └── log('ok')
```

调用栈本身就是上下文——栈帧一层层叠着，函数在任何深度都能顺着栈找到"最初是谁调的我"。

但异步把栈炸掉了。第 3 章讲过，回调执行时，原来的栈早已退栈；第 8 章又补了一刀：emit 是同步 for 循环，监听器拿到的调用栈属于"数据到达"这个事件，**不属于任何请求**。栈没了，"来龙去脉"就没了——这就是第 8 章 8.5 节的困境。

关键推论：既然栈靠不住，Node.js 必须把"来龙去脉"从栈里搬出来，存到一个**比栈活得久的地方**。这个地方就是本章的主角——异步因果链。

## 12.2 asyncId：每个异步操作的出生证明

Node.js 的做法朴素而彻底：**给每一个异步资源发一张出生证明**。

任何异步操作——定时器、文件读写、socket、Promise、甚至 nextTick 回调——在创建那一刻，运行时都分配给它一个全局唯一的编号 asyncId，同时记下"是谁创建了我"（triggerAsyncId）：

```
asyncId        = 我是谁
triggerAsyncId = 谁创建了我（创建我时，正在执行谁的回调）
```

于是整个进程里的异步操作构成一棵树：

```
HTTP 请求到达，执行请求回调        asyncId = 10
  ├── 回调里 setTimeout(...)       asyncId = 11，trigger = 10
  ├── 回调里 fs.readFile(...)      asyncId = 12，trigger = 10
  │     └── readFile 的回调里再 setImmediate(...)
  │                                asyncId = 13，trigger = 12
  └── ...
```

顺着 trigger 一路往上找，任何回调都能回答"我的祖先是谁"——第 8 章说的"异步族谱"，字面意思就是这张图。

这套出生证明由谁签发？回到第 2 章的机制：几乎所有内置异步对象的 C++ 侧都继承同一个基类 **AsyncWrap**（`src/async_wrap.cc`），它在构造时申领 asyncId 与 triggerAsyncId，析构时登记销毁。而第 2 章那个"话筒" MakeCallback 每次拉起 JS 回调时，会先进入一个 CallbackScope，把"当前正在执行的 asyncId"切换成该回调对应的值——**"当前上下文"就这样在一次次 C++→JS 的穿越中被维护着**。

## 12.3 async_hooks：族谱的观测窗

有了族谱，Node 把它开放成一个观测 API——async_hooks：

```js
const async_hooks = require('async_hooks');

async_hooks.createHook({
  init(asyncId, type, triggerAsyncId) {
    // 新异步资源诞生：type 如 Timeout / FSReqCallback / TCPWRAP
  },
  before(asyncId) { /* 该资源的回调即将执行 */ },
  after(asyncId)  { /* 回调执行完毕 */ },
  destroy(asyncId) { /* 资源销毁 */ },
}).enable();
```

四个钩子覆盖一个异步资源的完整生命周期。借助它们，诊断工具可以：在 init 里记下 `asyncId → triggerAsyncId` 的边，事后从任意回调沿 trigger 链回溯，还原出"这个回调的完整出身"——内存泄漏定位、句柄泄漏排查、请求级资源统计，全都建立在这上面。

但注意它的定位：**async_hooks 是显微镜，不是日常工具**。代价有三：

1. **性能**：钩子开启后所有异步操作都被插桩，吞吐可见下降；
2. **内存**：注册了 destroy/promiseResolve 钩子，Promise 等资源的销毁通知会被延迟到 GC 之后，内存水位随之上涨；
3. **侵入**：before/after 在热路径上反复触发，会干扰你对性能的真实观测。

所以生产代码几乎不直接碰 async_hooks——它是 APM 探针、诊断工具的地基。应用层要的是更便宜的答案，这就引出下一节。

### 12.3.1 AsyncResource：给自定义异步原语补一张出生证

async_hooks 是观测器，而 **AsyncResource**（`lib/async_hooks.js`）才是真正动手的那把螺丝刀——它让你可以**手动**给一个自定义的异步原语签发 asyncId，把它缝进族谱。

为什么需要它？因为运行时只给内置的定时器、I/O、Promise 发出生证；任何你自己造的异步原语——线程池任务、自己封装的回调分发器、第三方库里的自定义异步接口——天生不在族谱里。不补这张证，AsyncLocalStorage 就找不到它们，store 传播到那里就断。

用法很克制：

```js
const { AsyncResource } = require('async_hooks');

class MyWorkerTask {
  constructor(callback) {
    // 在创建时申领 asyncId，触发者 = 当前正在执行的资源
    this.resource = new AsyncResource('MyWorkerTask');
    this.callback = callback;
  }
  invoke(err, result) {
    // runInAsyncScope 让 callback 继承"创建时"的上下文
    this.resource.runInAsyncScope(this.callback, null, err, result);
    this.resource.emitDestroy();
  }
}
```

与 async_hooks 的关键区别：**AsyncResource 只补一张证，不会给所有操作插桩**——它没有 async_hooks 的全局开销。典型场景：

- 封装第三方异步原语（如数据库驱动、消息队列客户端）；
- 线程池任务调度：每个任务继承提交它时的上下文（官方文档的 Worker Pool 范例）；
- 流式处理中把任务分发到 worker 再收回时保持上下文连续。

记住这个分层：**AsyncResource 维护族谱本身，AsyncLocalStorage 在族谱上存值**。前者是基础设施，后者是应用层便利。理解了这一层，"上下文为什么能传播"就不再是黑盒——因为族谱被维护着，而 AsyncLocalStorage 只是它的上层建筑。

## 12.4 AsyncLocalStorage：应用层的标准答案

第 8 章给过它的使用形态，现在看它凭什么成立：

```js
const { AsyncLocalStorage } = require('async_hooks');
const als = new AsyncLocalStorage();

server.on('request', (req, res) => {
  als.run({ reqId: nextId() }, () => handle(req, res));
  //     └─ store：这个请求的上下文      └─ 整条异步子树的根
});

// 任意深度的异步回调里——定时器、I/O 回调、await 之后、emit 的监听器：
function log(msg) {
  console.log(`[req ${als.getStore()?.reqId}] ${msg}`);
}
```

`run(store, fn)` 的语义精确而强大：**在 fn 及其引发的整条异步调用链内，任何位置调用 getStore() 都返回 store**。出 run 之外，store 即刻失效；run 可以嵌套，内层遮蔽外层——语义与作用域如出一辙，只是这个"作用域"跨越了异步边界。

它是怎么做到的？底层有两套实现，恰好是一条演进线：

**第一代：基于 async_hooks 的族谱回溯。** run 时把 store 记在当前异步资源上；getStore 时沿 trigger 链向上查找，直到找到某个"登记过 store"的祖先。逻辑直白，但每次 getStore 都可能要走链上溯。

**第二代：AsyncContextFrame（帧随延续体传播）。** 既然每个异步边界都要查一次，不如让上下文**自己跟着走**：Node 与 V8 协作，把"当前上下文帧"直接挂进 Promise 的延续体与异步边界（`lib/internal/async_context_frame.js`、`src/async_context_frame.cc`）——await 恢复、定时器到期、回调入场时，帧自动就位，无需回查。第 3 章的微任务队列、timers、nextTick 队列都各自保存并恢复帧（`lib/internal/timers.js`、`lib/internal/process/tasks_queues.js` 中可见），这正是"所有异步边界都认得上下文"的原因。新实现开销已低到可默认开启、用于生产——第 8 章那句"开销已低到可默认用于生产"，底层依据就在这里。

两套实现在 `lib/internal/async_local_storage/` 下并存，接口完全一致，应用代码无感。**把复杂度压进运行时、把简单露给应用**——这是 Node 内部模块的一贯做派（第 10 章 primordials 也是同一立场）。

### 12.4.1 run 与 enterWith：作用域语义的两面

run 与 enterWith 是 AsyncLocalStorage 提供的两种进入作用域的方式，它们共享同一套传播通道，但作用域的几何形状相反。

`run(store, fn)` 是**子树作用域**：store 只在 fn 引发的异步子树内可见，fn 返回后作用域即刻收缩。fn 是同步或异步都行；当 fn 是 async 函数时，run 返回 Promise，await 这个 Promise 等于 await 整条异步链。

`enterWith(store)` 是**从此处起的作用域**：它不返回 Promise，而是把"当前正在执行的异步资源"切换到一个新的 store——从调用点起，包括后续所有同步代码和由它们触发的异步操作，都归属这个 store。它的作用域没有闭合边界，会一直向前污染，直到再次 enterWith 或进程结束。

这两种几何形状对应两类场景：run 适合"一段有明确起止的代码"，enterWith 适合"一个从此处开始、不再回到原上下文的新会话"（例如 WebSocket 连接建立的瞬间、长连接首次握手）。二者不是"好的/坏的"之分，而是作用域语义本身的两种合法形态——就像函数作用域与模块作用域一样。

### 12.4.2 run 与 async 函数的结合

run 的返回值就是 fn 的返回值。当 fn 是 async 函数时，run 返回 Promise——这意味着**run 一个 async 函数，其语义等价于 await 这整条异步链**。这是 AsyncContextFrame 与 V8 的 Promise 延续体协作的自然结果：async 函数内部每个 await 都是一个新的 Promise，每个 Promise 都在 run 的作用域内，所以每个 await 的恢复点都能通过 AsyncContextFrame 找回同一个 store。

反过来也导出一个机制约束：如果 run 一个 async 函数却**没有** await 它，调用方拿到的只是一个"还未 settle 的 Promise"，调用方继续往下执行——run 的作用域仍然覆盖那条未完成的异步链，但调用方已经脱离了它。这不是 bug，而是 run 的语义本身决定的——它只负责"在子树内传播 store"，不负责"让调用方等待"。忘记 await 带来的"失控感"，根源在于调用方对"是否等待子树完成"这件事做了错误的假设。

## 12.5 边界之外：上下文如何跨线程与进程

现在回到本章问题里最硬的部分。第 9 章说过：容器边界就是隔离边界。第 11 章说过：跨 Worker 只能传消息，跨进程只能走 IPC。那么——**ALS 的 store 能自己穿过去吗？**

答案干脆：**不能。** 族谱与帧都活在 Environment 内部；store 的传播半径就是"一个 Node 实例"。`new Worker()` 造出的是全新四件套（线程 + Isolate + Environment + 事件循环），对面那套异步世界从零开始，没有一条 trigger 边连回主线程。在 Worker 里调 getStore()，拿到的是 undefined。

这不是缺陷，而是第 9 章边界表的直接推论——"什么能共享、什么不能"由容器层级决定。要跨边界，就按第 11 章的规矩来：**把上下文当作普通数据，随消息显式携带，对面重新 run**：

```js
// ── 主线程 ──
als.run({ reqId: 42 }, () => {
  const store = als.getStore();
  worker.postMessage({ ...task, __ctx: { reqId: store.reqId } });  // 随消息带走
});

// ── Worker 线程 ──
parentPort.on('message', ({ __ctx, ...task }) => {
  als.run(__ctx, async () => {           // 在边界这头重新生根
    // 此后 Worker 内的所有异步回调，getStore() 都成立
  });
});
```

模式总结成一句话：**上下文不是流过去的，是带过去、在对岸重新生长的。** 跨进程的 child_process / cluster 同理——走环境变量或 IPC 消息携带，对面进程里重新 run。跨机器（微服务之间）再退一步：trace id 写进 HTTP 头（如 W3C 的 traceparent），下游服务收到后 run 起来。

于是得到一张完整的传播半径表：

| 边界 | 上下文自动传播？ | 接续方式 |
|------|:---:|------|
| 异步边界（回调 / await / emit） | ✅ 自动 | AsyncLocalStorage 本职 |
| Worker 线程（第 11 章） | ❌ | postMessage / workerData 携带 + 对侧 run |
| 子进程 / Cluster（第 11 章） | ❌ | env / IPC 携带 + 对侧 run |
| 跨机器 | ❌ | 协议头透传（traceparent）+ 对端 run |

规律一目了然：**每穿过一道容器边界，就需要一次"显式携带 + 重新 run"**。边界的清单在第 9 章，穿墙的手法在本章——两章合起来，才是"上下文串联"的完整答案。

## 12.6 多条因果链并存：上下文的多实例正交

run 与 getStore 总是绑定到"某一个 ALS 实例"——这个看似平凡的细节，其实暗含一条机制推论：**同一进程内可以存在多条独立的因果链**。

每个 `new AsyncLocalStorage()` 各自维护一份"run 时写入的 store"，互不覆盖。HTTP 入口若同时启动两条链——一条承载请求追踪（traceId），一条承载用户会话（userId）——在任意深度的异步回调里，两条链的 getStore 各自返回自己那条链最近一次 run 写入的 store。两个正交的上下文维度因此可以各自独立地跨越同一批异步边界，互不干扰。

这正是中间件架构（如 Koa 的洋葱模型、OpenTelemetry 的 span 栈）在底层依赖的机制：每一层中间件持有自己那条 ALS 实例，写入自己的上下文（请求属性、事务、鉴权信息），而所有实例共享同一张异步族谱、同一个 AsyncContextFrame 传播通道。**多实例的"多上下文"与单实例的"单上下文"不是两套规则，而是同一套规则在不同实例数量下的自然显形。**

附带一个对称的推论：同一个 ALS 实例若嵌套 run，内层的 store 会遮蔽外层——与作用域变量同名遮蔽是同一回事（内层 store 只包含自己写入的字段，外层的同名字段被"压住"）。分布式追踪系统每开一个新 span 都把父 span 的信息显式带进当前 store，就是为了不让这层遮蔽切断祖先链；这条约束同样来自作用域语义本身，而不是 API 的某种特殊行为。

## 12.7 工程落点：一条 trace 走天下

把三段传播半径拼起来，就得到现代后端"全链路追踪"在 Node 侧的完整地基。一次请求的入口处，用 run 把 traceId 绑进一个 ALS 实例；此后任意深度的异步回调、await、emit 的监听器里，日志函数都能通过 getStore 拿到同一个 traceId——不需要任何参数传递，异步机制自己把上下文带到了现场。跨 Worker 时 traceId 随消息携带、在对面重新 run；跨进程走 IPC 或环境变量；跨机器写进 HTTP 头（如 W3C 的 traceparent），下游服务收到后同样 run 起来。

需要人为干预的位置只有两类：**边界处**（消息里塞进 store、对侧重新 run）和**入口/出口处**（协议头读写）。中间的一切传播——跨回调、跨 await、跨 emit——运行时已经替你做完。排障时 grep 一个 traceId 就能还原一次请求的完整一生；APM 与分布式追踪（OpenTelemetry 的 Node SDK）内部正是这样：在入口处 run，在边界处携带，在日志与埋点处 getStore。

## 12.8 本质小结

> **一句话本质**：async_hooks 给每个异步资源发出生证明（asyncId + triggerAsyncId），织成一张因果族谱；AsyncLocalStorage 把"当前上下文"附着在这张族谱（或更高效的延续体帧）上自动传播，多个实例各自维护独立因果链；而容器边界（线程、进程）是它唯一的墙——穿墙靠"显式携带 + 对岸重新 run"。

要点：

1. **调用栈在异步边界处断裂**——上下文必须脱离栈、存到活得更久的地方。
2. **asyncId / triggerAsyncId 是异步族谱的边**——AsyncWrap 签发，MakeCallback 的 CallbackScope 维护"当前值"；async_hooks 是观测窗，AsyncResource 是补出生证的基础设施。
3. **AsyncLocalStorage 是应用层标准答案**——run 划域、getStore 取值；run(async fn) 返回 Promise；enterWith 仅用于"从此处起"的长会话场景。
4. **两代实现**：族谱回溯 → AsyncContextFrame 帧随延续体传播；新实现默认启用，生产可用。
5. **多实例正交、同实例遮蔽**——不同维度的上下文走不同 ALS 实例；同实例嵌套 run 遮蔽外层是作用域语义的自然结果，而非特殊行为。
6. **传播半径 = Environment 边界**——跨 Worker / 子进程 / 机器一律"显式携带 + 重新 run"；每道容器边界一次。
7. **store 最小化**——只放标识符与元数据；大对象走参数或按 ID 查，别塞进 store。

## 下一章引子

十二章，零件与容器、因果与边界，全部就位。是时候兑现前言的承诺了——

把所有机制串成一部完整的电影：一个 HTTP 请求，从网卡上的电信号，到你的回调函数，再到响应字节离开网卡。每一帧，都是前面某一章的机制在工作——包括本章这条悄悄贯穿全片的因果链。

终章：万物归一。

---

[← 上一章：多核之路](./ch11-multicore.md) | [终章：万物归一 →](../ch13-epilogue.md)
