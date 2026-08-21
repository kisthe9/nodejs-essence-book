# 附录

## A. 术语表

| 术语 | 一句话定义 | 出处 |
|------|-----------|------|
| Isolate | V8 的独立实例：独立堆、独立 GC，同一时刻只允许一个线程进入 | 第 1 章 |
| Context | Isolate 内的一套全局环境；vm 沙箱的基础 | 第 1 章 |
| Ignition / Sparkplug / Maglev / TurboFan | V8 分层编译管线：解释器 / 直译基线 / 中层优化 / 顶层优化编译器 | 第 1 章 |
| STW（Stop-The-World） | GC 暂停 JS 执行的时刻，直接计入请求延迟 | 第 1 章 |
| internalBinding | 内置 JS 模块获取 C++ 能力的唯一通道，用户代码不可见 | 第 2 章 |
| BaseObject | JS 对象与 C++ 对象一对一双向绑定的地基类 | 第 2 章 |
| MakeCallback | C++ 世界调用 JS 回调的统一入口（"底层向 JS 喊话的话筒"） | 第 2 章 |
| FunctionTemplate | 把 C++ 函数铸成 JS 函数的 V8 模具；internalBinding 的导出皆出于此 | 第 2 章 |
| CallbackScope | MakeCallback 三段式之首：进场时切换异步上下文；TryCatch 兜住 JS 异常 | 第 2 章 |
| 事件循环 | libuv uv_run 的七阶段循环，Node 异步的心脏 | 第 3 章 |
| poll 阶段 | 循环的主腔：调用 epoll_wait 向内核收割就绪事件，空闲时在此阻塞 | 第 3 章 |
| 微任务 | nextTick 队列与 Promise 队列，在阶段间隙排空，可饿死循环 | 第 3 章 |
| uv_run 三模式 | DEFAULT 转到没活 / ONCE 转一圈可阻塞 / NOWAIT 转一圈不阻塞；Node 用 DEFAULT | 第 3 章 |
| epoll | Linux 的 I/O 多路复用机制：成本只与就绪事件数相关 | 第 4 章 |
| EAGAIN | 非阻塞 fd "暂时无数据"的返回码；边缘触发下读到它才停 | 第 4 章 |
| 线程池 | libuv 默认 4 线程，替主线程执行阻塞操作（文件/DNS/部分 crypto） | 第 4 章 |
| fd | 进程私有的整数号码牌，指向内核 struct file | 第 5 章 |
| inode | 内核中资源的本体；socket/pipe 的 inode 是内存匿名对象 | 第 5 章 |
| SCM_RIGHTS | 通过 Unix 域套接字把 fd 传给另一个进程的机制 | 第 5 章 |
| dup2 | 重定向的本质：fork 后 exec 前改写 fd 表项的指向 | 第 5 章 |
| NODE_CHANNEL_FD | fork 时用环境变量向子进程交接 IPC 通道的 fd 号码 | 第 5 章 |
| EMFILE | fd 表耗尽错误；fd 泄漏的雪崩终点 | 第 5 章 |
| BackingStore | ArrayBuffer 持有的堆外裸内存；Buffer 零拷贝的物理基础 | 第 6 章 |
| allocUnsafe | 不清零的快速分配；残留数据是真实安全风险 | 第 6 章 |
| highWaterMark | 流内部缓冲的水位线；"建议停"而非硬上限 | 第 7 章 |
| 背压 | write 返回 false + 'drain' 组成的反向刹车信号，可传导至 TCP 窗口 | 第 7 章 |
| pipeline | 带错误传播与全链销毁的流组装函数，生产首选 | 第 7 章 |
| emit | 同步 for 循环分发监听器；异步性来自"何时被调用" | 第 8 章 |
| AsyncLocalStorage | 跨异步边界携带请求上下文的标准机制 | 第 8、12 章 |
| Environment | "一个 Node.js 实例"的 C++ 真身：事件循环 + 子系统 + 清理队列 | 第 9 章 |
| Realm | Context + process + 模块缓存的打包；主 Realm 住着你的代码 | 第 9 章 |
| primordials | 启动时保存的内建对象纯净副本，防原型污染 | 第 10 章 |
| 快照（snapshot） | 构建期预执行引导脚本后序列化的 V8 堆，启动时直接恢复 | 第 10 章 |
| 包壳（wrapper） | 模块源码外的函数壳：用户模块五参；内置模块多 internalBinding 与 primordials 两参 | 第 2、10 章 |
| beforeExit / exit | 循环空后的挽留机会（可多次）/ 只许同步代码的遗言时刻 | 第 10 章 |
| 结构化克隆 | postMessage 跨 Isolate 传值的序列化复制机制 | 第 11 章 |
| Transferable / SharedArrayBuffer | 内存过户（零拷贝）/ 唯一真共享内存（需 Atomics） | 第 11 章 |
| asyncId / triggerAsyncId | 异步资源的"我是谁"/"谁创建了我"，织成异步因果族谱 | 第 12 章 |
| AsyncWrap | C++ 侧异步资源基类，签发 asyncId 族谱的出生证明 | 第 12 章 |
| async_hooks | 异步族谱的观测 API（init/before/after/destroy）；代价不低，留给诊断工具 | 第 12 章 |
| AsyncContextFrame | 把上下文帧挂进 Promise 延续体的第二代实现，免回溯、默认启用 | 第 12 章 |

## B. 易混淆速辨

| 常见误解 | 事实 | 详见 |
|---------|------|------|
| "Node.js 是单线程的" | JS 执行单线程；进程内另有线程池、GC 线程、平台线程 | 第 1、4 章 |
| "事件驱动 = 异步" | emit 是同步 for 循环；异步的是事件的触发时机 | 第 8 章 |
| "所有异步 I/O 都走事件通知" | 只有网络走 epoll；文件/dns.lookup 走线程池模拟 | 第 4 章 |
| "setTimeout(fn,0) 先于 setImmediate" | 主模块顶层顺序不定；I/O 回调内 setImmediate 必先 | 第 3 章 |
| "fd 就是文件/连接本身" | fd 只是号码牌；本体是内核 inode | 第 5 章 |
| "IPC 是进程间发消息" | 本质是多个 fd 指向同一个内核对象 | 第 5 章 |
| "重定向是程序改了输出" | 程序零感知：shell 在 fork 后 exec 前用 dup2 换掉 fd 表指向 | 第 5 章 |
| "Buffer.length 是字符数" | 是字节数；多字节字符两者不等 | 第 6 章 |
| "highWaterMark 是缓冲上限" | 只是建议水位；无视 write 返回 false 照样 OOM | 第 7 章 |
| "uncaughtException 可以用来续命" | 只该记录现场 + 优雅退出；进程状态已不可信 | 第 8、10 章 |
| "process 是全局魔法对象" | 是 Environment 的 JS 投影，启动第③步才诞生 | 第 9、10 章 |
| "require 是全局函数" | 每个模块一份私有 require，诞生时记住本模块位置 | 第 2、10 章 |
| "process.env 是启动时的一份拷贝" | 是进程环境表的实时代理，读写直达 getenv/setenv | 第 10 章 |
| "process.exit() 是正常退出方式" | 是拉闸；会丢异步缓冲。正道是撤掉活跃句柄 | 第 10 章 |
| "Worker 之间共享变量" | 堆隔离；postMessage 是克隆，共享只有 SharedArrayBuffer | 第 11 章 |
| "AsyncLocalStorage 能自动跨线程传播" | store 的传播半径是一个 Environment；跨 Worker/子进程需随消息携带 + 对侧重新 run | 第 12 章 |
| "async_hooks 适合业务代码日常使用" | 它是诊断工具的地基：插桩开销与内存代价都明显，应用层用 AsyncLocalStorage | 第 12 章 |

## C. 七机制 → 常见子系统映射

本书未展开的子系统，全部是七个核心机制的组合应用：

| 子系统 | 用到的机制 |
|--------|-----------|
| HTTP/1.1、HTTP/2 | fd + Stream + EventEmitter + 事件循环（HTTP/2 另有多路复用帧层） |
| TLS | Duplex 流（明文侧/密文侧两套缓冲）+ crypto 的 C++ Binding |
| crypto | Binding（OpenSSL 封装）+ 部分操作走线程池 |
| dgram（UDP） | fd + epoll（无连接，无 Stream 语义） |
| WebSocket（ws 库） | Duplex + Buffer 二进制帧解析 |
| REPL / CLI | TTY 的 fd 特殊处理 + 生命周期 |
| vm 模块 | 第 9 章的 Realm/Context 机制 |
| WASI / wasm | Isolate 内的另一种可执行格式，仍受同一约束 |
| npm / 包管理 | 纯应用层，与运行时机制无关 |

## D. 延伸阅读

- **官方文档**：nodejs.org 的 Event Loop、Stream、Worker Threads 专题指南——权威且随版本更新。
- **libuv 设计文档**：docs.libuv.org 的 Design Overview——事件循环与线程池的第一手描述。
- **V8 官方博客**：v8.dev/blog——Ignition/TurboFan/Orinoco 的设计文章均出自引擎作者。
- **Linux 手册页**：`man 7 epoll`、`man 2 open`、`man 7 unix`（SCM_RIGHTS 在此）——内核语义的最终裁决者。
- **Node.js 源码**（配合本书地图）：`lib/` 门内 JS → `src/` 门后 C++ → `deps/uv` 心脏 → `deps/v8` 隔离舱。建议的第一条源码阅读路线：`lib/net.js` 的 `listen` → `lib/internal/net.js` → `src/tcp_wrap.cc`。

---

[← 终章：万物归一](./ch13-epilogue.md) | [返回目录](./README.md)
