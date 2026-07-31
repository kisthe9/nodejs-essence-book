# 第 9 章 运行时容器

> **本章问题**：`process` 这个不用 require 就存在的对象，是谁造的？"一个 Node.js 实例"在底层对应什么实体？前八章的零件，装在什么里面？

## 9.1 从 process 的身世查起

每个 Node.js 程序员每天都在用 `process`——`process.env`、`process.exit()`、`process.on('SIGINT')`。它无处不在，却没人 require 过它。全局对象里凭空出现的东西，一定有人在你的代码运行之前把它放好了。

顺着这条线索深挖，会挖出 Node.js 运行时的三层容器结构：

```
┌────────────────────────────────────────────────────────┐
│ V8 Isolate（第 1 章的隔离舱：独立堆、独立 GC、单线程）        │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Environment（Node.js 实例的"真身"，C++ 类）          │  │
│  │  · 持有事件循环 uv_loop_t（第 3 章的心脏）            │  │
│  │  · 持有清理队列（进程退出时按序销毁资源）               │  │
│  │  · 持有 Inspector、权限控制等子系统                   │  │
│  │                                                  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │ Realm（绑定一个 V8 Context 的执行域）          │  │  │
│  │  │  · process 对象住在这里                       │  │  │
│  │  │  · 已加载的内置模块缓存住在这里                  │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

| 容器 | 来自谁 | 装什么 |
|------|--------|--------|
| Isolate | V8 | JS 堆、GC——语言层的隔离单位 |
| Environment | Node.js（`src/env.cc`） | 事件循环、资源清理队列、各子系统——**"一个 Node 实例"的实体** |
| Realm | Node.js | process 对象、模块缓存——一个 Context 里的运行状态 |

**Environment 才是"一个 Node.js"的真身。** V8 只提供了 JS 的执行与内存（Isolate），Node 把自己的一切——心脏（事件循环）、门（Binding 注册表引用）、生命周期管理——全部聚合进 Environment 这个 C++ 对象。所谓"启动一个 Node 实例"，就是创建一个 Environment 并把它跑起来。

这个设计的深意在第 11 章才完全显形：既然"一个 Node 实例"被干净地封装成了一个 C++ 对象，那么**在同一个进程里创建第二个、第三个实例**就成为可能——这正是 Worker Threads 的实现前提。一个 Worker = 一个新线程 + 一个新 Isolate + 一个新 Environment。

## 9.2 process：Environment 伸进 JS 的手

回到开头的问题。process 对象在启动早期（下一章会看到确切时机）由引导代码创建，挂到全局。它的本质是：**Environment 里各种 C++ 状态与能力，以 JS 属性和方法的形式露出的投影。**

| 你调用的 | 背后发生的 |
|---------|-----------|
| `process.env.HOME` | 读进程环境变量表（C++ 侧持有） |
| `process.memoryUsage()` | 穿过 Binding 查询 V8 堆统计与系统内存信息 |
| `process.exit(1)` | 调 Environment 的退出流程：跳过事件循环、执行清理、终止进程 |
| `process.on('SIGINT')` | 注册信号监听——底层通过 libuv 的信号句柄挂进事件循环 |
| `process.nextTick(fn)` | 往第 3 章那个最高优先级队列里塞回调 |

留意最后两行：process 同时是一个 EventEmitter（第 8 章的继承者名单里见过它）。信号（SIGINT/SIGTERM）、生命周期节点（beforeExit/exit）、兜底错误（uncaughtException）都以事件形式从它身上发出。**process = Environment 的状态投影 + 进程级事件的发射器**，两种身份合一。

## 9.3 为什么需要 Realm 这一层？

Isolate 和 Environment 之间再隔一层 Realm，初看多余，其实对应着一个真实需求：**同一个 Node 实例里可以有多个 JS 全局环境**。

第 1 章提过 `vm` 模块能创建"干净的全局环境"（新 Context）。每个 Context 需要配套的状态——它自己的内置模块缓存、它自己的错误处理设施。Realm 就是"一个 Context + 它的配套状态"的打包。主 Realm 装着你的 process 和主模块；`vm` 或内嵌场景可以有附属的 Realm。对日常开发，你只需要记住：**你的代码活在主 Realm 里，process 是主 Realm 的住户。**

## 9.4 容器的边界就是隔离的边界

三层容器各自划出一条隔离边界，边界决定了"什么能共享、什么不能"：

```
线程边界   = Isolate 边界    两个 Isolate 不共享 JS 堆
                             → Worker 之间不能直接传对象（第 11 章）
实例边界   = Environment 边界 两个 Environment 各有事件循环
                             → 各自的定时器、I/O 互不干扰
全局边界   = Realm 边界       两个 Realm 各有全局对象
                             → vm 沙箱里改 global 不影响主环境
```

这张表值得收藏：Node.js 中一切"为什么 A 看不到 B"的问题——Worker 里拿不到主线程的变量、vm 里的全局污染不出来、两个子进程互不影响——答案都是"它们隔着某层容器边界"。

## 9.5 本质小结

> **一句话本质**：Environment 是"一个 Node.js 实例"的 C++ 真身——它把事件循环、Binding、清理队列聚合成一个可整体创建/销毁的容器；process 只是它伸进 JS 世界的手。

要点：

1. **三层容器**：Isolate（V8 的堆与执行隔离）⊃ Environment（Node 实例：事件循环 + 子系统）⊃ Realm（Context + process + 模块缓存）。
2. **process 是投影不是本体**——它的每个方法背后都是 Environment/Binding 的 C++ 状态与操作。
3. **process 兼任进程级 EventEmitter**——信号、生命周期、兜底错误都从它 emit。
4. **Realm 支撑多全局环境**——vm 沙箱的实现基础；你的代码住在主 Realm。
5. **容器边界 = 隔离边界**——"谁看不到谁"的问题，答案总在某层容器的边界上。

## 下一章引子

容器的结构清楚了，但还是静态的图纸。从你敲下 `node app.js` 回车，到你的第一行代码执行，中间这几十毫秒里，这套容器是怎么被搭建起来的？`process` 具体在哪一步出现？为什么 Node.js 的启动能这么快？

而进程的另一头——退出——同样值得琢磨：为什么有时 `beforeExit` 会触发多次？为什么 `process.exit()` 会丢日志？

下一章：生命周期，从出生到退场。

---

[← 上一章：EventEmitter](../part-3-data/ch08-eventemitter.md) | [下一章：生命周期 →](./ch10-lifecycle.md)
