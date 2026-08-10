# 第 11 章 多核之路：复制容器，而非共享内存

> **本章问题**：单线程只能用一个核。Node.js 想吃满 64 核机器，在"不打破单线程约束"的前提下，路在哪里？

## 11.1 只有一种答案的选择题

传统多线程语言（Java/C++）的答案是共享内存：多个线程读写同一堆数据，用锁维持秩序。这条路 Node.js 走不了——第 1 章的 Isolate 规则堵死了它：**JS 堆不允许第二个线程进入**。

那就只剩一种答案：**不共享，复制。** 把第 9 章封装好的"容器"整个再造一份，让每份容器独占一个核，容器之间只靠**传递消息**协作。

这个答案有两种规格，对应两层容器边界：

```
规格一：Worker Threads（线程级复制）
┌─ 进程 ──────────────────────────────────────┐
│  主线程                    Worker 线程         │
│  ┌──────────────┐        ┌──────────────┐   │
│  │ Isolate A     │        │ Isolate B    │   │
│  │ Environment A │ <────> │ Environment B│   │
│  │ 事件循环 A     │  消息   │ 事件循环 B    │   │
│  └──────────────┘        └──────────────┘   │
└─────────────────────────────────────────────┘
   同一进程内：可共享一种特殊内存（后述）

规格二：Cluster / child_process（进程级复制）
┌─ 进程 1 ─────────┐      ┌─ 进程 2 ─────────┐
│ 完整的 Node 实例  │<────>│ 完整的 Node 实例   │
└─────────────────┘  IPC  └─────────────────┘
   彻底隔离：一个崩了另一个毫发无损
```

第 9 章的伏笔在此兑现：正因为"一个 Node 实例"被干净封装成 Environment，Worker Threads 才可能实现——`new Worker()` 的本质就是：**新线程 + 新 Isolate + 新 Environment + 新事件循环**，四件套一起造。

## 11.2 Worker Threads：同屋分居

```js
const { Worker, isMainThread, parentPort } = require('worker_threads');

if (isMainThread) {
  const w = new Worker(__filename);
  w.postMessage({ n: 45 });
  w.on('message', (result) => console.log('fib =', result));
} else {
  parentPort.on('message', ({ n }) => parentPort.postMessage(fib(n)));
}
```

主线程照常处理请求，Worker 在另一个核上算 fib(45)——第 1 章那个"CPU 密集卡死一切"的困局，在这里解开。

### postMessage 传的不是引用

两个 Isolate 堆互不相通，所以 `postMessage(obj)` 实际执行的是：**结构化克隆**——把对象序列化、穿越线程边界、在对方堆里重建副本。改副本不影响原件。这也标出了 Worker 的成本模型：

- **创建贵**：四件套（线程/Isolate/Environment/循环）不是轻量协程，常驻 Worker 池是标准用法；
- **传输贵**：大对象克隆耗时可观。两条省钱通道：
  - **Transferable**：ArrayBuffer 可以"过户"——内存所有权移交对方，本侧失效，零拷贝；
  - **SharedArrayBuffer**：唯一的例外，一块**真正共享**的裸内存。多线程同时读写它会怎样？欢迎回到锁与竞态的世界——需要 Atomics 原子操作配合。它是留给极致性能场景的后门，不是常规通道。

### 何时用 Worker

一条实用判据：**任务的计算时间 >> 数据的克隆时间**，Worker 才划算。压缩、加密、图像处理是典型正例；"每个请求开个 Worker 算个 JSON.parse"是典型反例（克隆比计算还贵）。

## 11.3 Cluster：分身服务同一个端口

CPU 密集用 Worker，而 Web 服务的诉求不同：请求本身是 I/O 密集的，单实例就够快，问题是**一个实例只吃一个核**。答案是进程级复制——cluster 模块：

```js
const cluster = require('cluster');
const os = require('os');

if (cluster.isPrimary) {
  for (let i = 0; i < os.availableParallelism(); i++) cluster.fork();
} else {
  http.createServer(handler).listen(8080);   // 所有 worker 听"同一个"端口？
}
```

8 个进程同时 `listen(8080)` 却不报端口冲突——第 5 章已经给过谜底：**主进程创建监听 socket，把 listen-fd 通过 SCM_RIGHTS 寄给每个 worker**；所有 worker 的 fd 指向同一个内核监听队列，内核负责把新连接分给某一个 worker。cluster 只是把第 5 章的 fd 传递机制包装成了三行代码。

进程级隔离还带来免费的容错：一个 worker 崩溃（毕竟第 8 章说过没人听的 error 会杀进程），其余 worker 不受影响，主进程监听 `'exit'` 事件补招一个新的——**自愈式架构**用 cluster 十行代码就能搭出来。

## 11.4 两种规格怎么选

| | Worker Threads | Cluster / 多进程 |
|---|---|---|
| 复制粒度 | 线程（同进程） | 整个进程 |
| 隔离强度 | 中：崩溃可能拖累进程 | 高：彻底隔离，单点崩溃不扩散 |
| 通信 | postMessage 克隆 / Transferable / SharedArrayBuffer | IPC 管道（JSON 序列化）/ 传 fd |
| 内存开销 | 较低（共享进程资源） | 较高（每进程完整实例） |
| 适合 | CPU 密集计算的卸载 | Web 服务吃满多核 + 容错 |

经验法则：**算东西，Worker；扛流量，Cluster**；两者可叠加（每个 cluster worker 内部再养 Worker 池）。生产部署中，K8s 单 Pod 单进程 + 副本数扩展，是把 cluster 的思路上移到编排层——原理同一个：复制实例，分发流量。

## 11.5 回望：约束的完整答卷

至此可以回望全书的推导链。第 1 章的约束（一个 Isolate 一个线程）从未被打破，Node.js 对它的完整答卷是：

```
纵向榨干一个核：事件循环 + 异步 I/O        （第 2、3、4 章）
     —— 让唯一的线程永不空等

横向复制到多核：Worker / Cluster          （本章）
     —— 容器随便复制，消息传递协作

数据层的配合：fd 通道 + Buffer 载体 + Stream 流控 + EventEmitter 分发
                                          （第 5、6、7、8 章）
容器层的支撑：Environment 封装 + 生命周期管理
                                          （第 9、10 章）
上下文的串联：asyncId 族谱 + AsyncLocalStorage 跨边界传播
                                          （第 12 章）
```

**单线程从来不是 Node.js 的弱点宣言，而是它的架构公理**——所有机制都从它推导出来，所有机制也都在补偿或放大它。

## 11.6 本质小结

> **一句话本质**：多核之路只有一条——复制容器、传递消息；Worker 在线程级复制（可选共享内存后门），Cluster 在进程级复制（借 fd 传递共享端口），共享内存的多线程模型被 Isolate 从根上排除。

要点：

1. **Worker = 新线程 + 新 Isolate + 新 Environment + 新循环**——第 9 章容器封装的直接兑现。
2. **postMessage 是克隆不是引用**——大数据用 Transferable 过户或 SharedArrayBuffer（需 Atomics）。
3. **Worker 划算判据：计算时间 >> 克隆时间**；常驻池是标准用法。
4. **cluster 共享端口 = SCM_RIGHTS 传 listen-fd**（第 5 章机制的三行封装）；进程隔离免费送容错。
5. **算东西 Worker，扛流量 Cluster**——可叠加，也可上移到 K8s 编排层。

## 下一章引子

十二章零件与容器全部就位。是时候兑现前言的承诺了——

把所有机制串成一部完整的电影：一个 HTTP 请求，从网卡上的电信号，到你的回调函数，再到响应字节离开网卡。每一帧，都是前面某一章的机制在工作。

不过，在开拍之前还有一个悬而未决的问题。第 8 章留下过它：回调跨过异步边界后，"我在为谁工作"就断了；本章又立起线程、进程一道道高墙。那么"来龙去脉"还能找回来吗？上下文能不能穿过 Worker 的边界？

下一章，先把这条贯穿全书的暗线——异步因果链——接上。

---

[← 上一章：生命周期](./ch10-lifecycle.md) | [下一章：异步上下文 →](./ch12-async-context.md)
