# Node.js 本质

> **从一个约束推导出整个运行时**

---

## 这本书讲什么

大多数 Node.js 书籍按模块划分章节：一章讲 fs，一章讲 http，一章讲 stream。读完之后你知道每个 API 怎么用，却回答不了这样的问题：

- 为什么 Node.js 偏偏是单线程的？
- 为什么读文件走线程池，而收网络包却不用？
- 为什么 `write()` 一个文件和 `write()` 一个 socket 是同一个系统调用？
- 为什么 `emit()` 是同步的，Node.js 却号称异步？

本书不按模块划分，而按**因果**划分。全书从一个事实出发——**JavaScript 在 V8 里单线程执行**——然后一步一步推导：这个约束逼出了什么设计，那个设计又留下了什么新问题，新问题又催生了什么机制。读到最后一章，你会看到全部机制收拢成一条线：一个 HTTP 请求从网卡到回调函数的完整旅程。

## 目录

### 前言

- [前言：为什么写这本书，怎么读这本书](./preface.md)

### 第一部 起点：一个约束

> JS 单线程是全书的第一因。这一部讲清楚这个约束从哪来（V8），以及被约束的 JS 如何突围（Binding）。

- [第 1 章 单线程的枷锁与馈赠](./part-1-constraint/ch01-single-thread.md) —— V8 如何执行 JS，单线程为何是一切设计的原点
- [第 2 章 沙箱之外](./part-1-constraint/ch02-beyond-sandbox.md) —— 模块系统组织代码，Binding 打通操作系统，回调在此封装

### 第二部 心跳：让单线程活起来

> 有了系统能力还不够——单线程一旦等待 I/O 就是死路。这一部讲 Node.js 的心脏如何跳动。

- [第 3 章 事件循环：心脏的七个瓣膜](./part-2-heartbeat/ch03-event-loop.md) —— uv_run 七阶段与回调优先级
- [第 4 章 两条 I/O 之路](./part-2-heartbeat/ch04-two-io-paths.md) —— 网络走 epoll，磁盘走线程池，以及为什么必须如此

### 第三部 血液：数据的形态与流动

> 心脏泵的是血。这一部讲数据在 Node.js 里以什么形态存在（fd、Buffer），如何流动（Stream），由谁分发（EventEmitter）。

- [第 5 章 fd：内核眼中的万物](./part-3-data/ch05-fd.md) —— 文件、Socket、管道为什么是同一个东西；stdio 的由来与 IPC 接力
- [第 6 章 Buffer：跨越两个世界的数据货币](./part-3-data/ch06-buffer.md) —— JS 与内核之间的零拷贝字节容器
- [第 7 章 Stream：有限内存处理无限数据](./part-3-data/ch07-stream.md) —— 分块、缓冲与背压
- [第 8 章 EventEmitter：事件驱动的字面实现](./part-3-data/ch08-eventemitter.md) —— 同步分发、error 铁律与异步上下文

### 第四部 容器：生命与繁衍

> 零件都齐了，谁把它们装起来？这一部讲运行时容器的结构、生命周期、多核扩展，以及穿越这一切的异步因果链。

- [第 9 章 运行时容器](./part-4-container/ch09-runtime-container.md) —— Isolate、Environment、Realm 与 process 的真身
- [第 10 章 生命周期](./part-4-container/ch10-lifecycle.md) —— 从 Bootstrap 到优雅退出；process 的诞生与模块火把交接
- [第 11 章 多核之路](./part-4-container/ch11-multicore.md) —— Worker Threads 与 Cluster：复制容器，而非共享内存
- [第 12 章 异步上下文：穿越边界的因果链](./part-4-container/ch12-async-context.md) —— async_hooks 族谱与 AsyncLocalStorage：串联异步回调、线程与进程

### 终章与附录

- [第 13 章 万物归一：一个请求的一生](./ch13-epilogue.md) —— 全书机制串成一条线，以及可以带走的设计原则
- [附录](./appendix.md) —— 术语表、易混淆速辨、延伸阅读

## 全书地图

```
              第一部（约束）              第二部（心跳）
  V8 单线程 ──逼出──> Binding 破壁 ──支撑──> 事件循环 ──调度──> 两条 I/O 路
      │                                                          │
      │ 第四部（容器）                    第三部（血液）           │
      └── Environment 容器 <──装载── EventEmitter <──分发── Stream/Buffer <──承载── fd
                │
                └──> 生命周期 ──> 多核（复制容器）──> 异步上下文（串联边界）──> 终章：一个请求的一生
```

暗线（一个回调的一生，穿越四道边界）：

```
 [2] 封装·语言边界 → [3] 瓣膜放行·时间边界 → [5] 管道接力·进程边界 → [12] 验照·因果边界
```

## 如何阅读

- **顺序读**：全书是一条因果链，每章开篇的问题来自上一章的结尾。第一次读建议按顺序。
- **跳着读**：每章自成一体，开篇有"本章问题"，结尾有"本质小结"，可按需查阅。
- **只读小结**：赶时间时，读每章最后的"本质小结"，30 分钟过完全书骨架。
