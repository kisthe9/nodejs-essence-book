# 第 7 章 Stream：有限内存处理无限数据

> **本章问题**：一个 2GB 的文件、一条永不结束的 TCP 连接——数据比内存大、甚至没有尽头时，程序怎么处理它？以及：上游生产比下游消费快时，多出来的数据堆在哪？

## 7.1 从一次内存爆炸说起

一个文件下载服务最直观的写法：

```js
// 反面教材
http.createServer((req, res) => {
  fs.readFile('/data/2gb-video.mp4', (err, data) => {
    res.end(data);   // data 是一个 2GB 的 Buffer
  });
});
```

10 个并发请求 = 20GB 内存。进程死于 OOM。

问题不在 readFile，在于"**把数据当作一块**"的思维。数据其实可以是水流：从文件读一小块、发给客户端、放手、再读下一块——任何时刻内存里只有一小块。这就是 Stream：

```js
http.createServer((req, res) => {
  fs.createReadStream('/data/2gb-video.mp4').pipe(res);
});
// 内存占用：每连接几十 KB，与文件大小无关
```

fd 给了我们字节接口（第 5 章），Buffer 给了字节容器（第 6 章），Stream 在两者之上补齐五种能力：**分块、缓冲、背压、统一接口、标准事件**。前四个本章讲，"标准事件"的机制是下一章的主角。

## 7.2 四种流，一个家族

```
EventEmitter                ← 所有流都是事件发射器（第 8 章）
    └── Stream
          ├── Readable      数据的源头       fs.createReadStream, http 请求体
          ├── Writable      数据的去处       fs.createWriteStream, http 响应
          ├── Duplex        既是源又是去处    net.Socket（读写两个方向、两套缓冲，互相独立）
          │     └── Transform  中途加工站    zlib.createGzip, crypto 流
          └── (PassThrough)    什么都不做的 Transform，常用于观测/计数
```

值得注意 Duplex 的结构：TCP socket 天然是双向的——你读到的和你写出的是两条独立的数据流。Duplex 因此内部持有**两套互不相干的缓冲区**，Readable 一套、Writable 一套。而 Transform 是特殊的 Duplex：写入侧进来的数据，加工后从读取侧出去——两套缓冲被一个加工函数打通。

每个流内部都有一个缓冲区和一条水位线（`highWaterMark`，字节流默认 64KB 或 16KB，视流类型而定）。缓冲区是"分块"与"背压"之间的减震器。

## 7.3 背压：Stream 的灵魂

### 问题

生产者和消费者速度几乎永远不相等。快磁盘读 → 慢网络发；快网络收 → 慢磁盘写。不加控制的话，差额会以每秒几十 MB 的速度在内存里堆积——OOM 只是时间问题。

### 机制

Stream 的解法是一套**自动的反向刹车信号**，核心只有两个约定：

```
约定一：writable.write(chunk) 有返回值
        true  = 缓冲区还有空位，继续来
        false = 缓冲区已到水位线，请停一停（数据我收下了，但别再发）

约定二：缓冲区排空后，writable 发出 'drain' 事件 = 可以继续了
```

pipe（以及现代的 `stream.pipeline`）把这两个约定接成了自动化闭环：

```
readable.pipe(writable) 内部逻辑：

  readable ──data──> writable.write(chunk)
                        │
              返回 false？
                        │ 是
                        ▼
              readable.pause()      ← 上游停止读取
                        │
              等 writable 'drain'
                        ▼
              readable.resume()     ← 恢复
```

### 刹车一路踩到底层

真正精彩的是刹车不止步于 JS 层。`readable.pause()` 会向下传导：

```
JS: pause()
 └─> C++: 停止 libuv 的读取（uv_read_stop）
      └─> libuv: 把 fd 从 epoll 关注列表移除（不再收"可读"通知）
           └─> 内核: socket 接收缓冲区渐满，无人来取
                └─> TCP: 通告窗口缩小 → 发送端减速/停发
                     └─> 对端机器: 感知到压力，它的写也开始返回 false…
```

**背压能穿透 JS、C++、内核，一路传到网线对面的发送端。** 从下载服务的慢客户端，到你的服务器，到上游的源站——整条链路上每一环的内存都被水位线约束着。这是"有限内存处理无限数据"的完整含义：不是靠更大的缓冲，而是靠**让整条流水线以最慢一环的速度运转**。

### 不用 pipe 时，你就是刹车

手写 write 循环时，忽略返回值等于剪断刹车线：

```js
// 反面教材：写入 1GB，无视返回值
for (const chunk of chunks) dest.write(chunk);   // 全部堆进内部缓冲区

// 正确姿势
const { once } = require('events');
for (const chunk of chunks) {
  if (!dest.write(chunk)) {
    await once(dest, 'drain');   // 等缓冲排空再继续
  }
}
```

内部缓冲区**没有硬上限**——highWaterMark 只是"建议停"的水位线，write 永远收下数据。所以"Stream 也会 OOM"的事故，几乎全是无视 false 造成的。

## 7.4 组装流水线

```js
const { pipeline } = require('stream/promises');

await pipeline(
  fs.createReadStream('access.log'),   // 源
  zlib.createGzip(),                   // 加工：压缩
  fs.createWriteStream('access.log.gz') // 汇
);
```

用 `pipeline` 而不是链式 `pipe` 的理由：pipe 不处理错误传播——链条中任何一环出错，其他环不会自动关闭，fd 与内存就地泄漏；pipeline 保证**任何一环失败，整条链全部正确销毁**，并把错误交给 await/回调。生产代码请默认 pipeline。

流水线上每个节点间流动的 chunk，就是上一章的 Buffer（objectMode 除外）。Buffer 管"数据是什么"，Stream 管"数据怎么流"——两章在此合拢。

## 7.5 本质小结

> **一句话本质**：Stream 把"数据是一块"换成"数据是一列"，再用背压让整条流水线自动降速到最慢一环的速度——内存占用从此与数据总量无关，只与水位线有关。

要点：

1. **四种流一个家族**：Readable/Writable/Duplex/Transform，全部继承 EventEmitter；Duplex 两套独立缓冲。
2. **背压 = write 返回 false + 'drain' 事件**的自动闭环；pipe/pipeline 替你接好这个闭环。
3. **刹车穿透到 TCP 窗口**——pause 传导至 epoll 注销与内核缓冲，压力能传到网线对面。
4. **缓冲区没有硬上限**——无视 write 的 false 返回值是 Stream OOM 的头号原因。
5. **生产代码用 pipeline**——错误时全链销毁，pipe 不管这事。

## 下一章引子

数据在流水线里流动，靠什么驱动？翻开任何一个流的代码：`'data'`、`'end'`、`'drain'`、`'error'`——全是事件。而流只是继承者之一：socket、server、子进程、process 对象本身，Node.js 里几乎每个 I/O 对象都在 emit 和 on。

是时候看看这个所有对象共同的祖先了。它出人意料地简单——简单到它的核心是一个同步 for 循环；也出人意料地危险——一个没人监听的 'error' 事件，就能让整个进程当场死亡。

下一章：EventEmitter。

---

[← 上一章：Buffer](./ch06-buffer.md) | [下一章：EventEmitter →](./ch08-eventemitter.md)
