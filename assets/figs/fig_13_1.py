"""图 13-1 内存账本：rss ⊃ heapTotal ⊃ heapUsed，堆外另册。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-13-1.svg")
C = F.C

parts = [F.header(820, "进程内存的两本账", "RSS ⊃ HEAP ⊃ USED")]

# 外框：rss
parts.append(F.zone(46, 76, 728, 330, "rss · 进程驻留内存 · 一切之和"))

# V8 堆
parts.append(F.box(66, 112, 380, 272, "", fill=C["card"], stroke=C["ink2"]))
parts.append(F.note(82, 136, "V8 堆 · heapTotal（已申请）", size=12.5))
parts.append(F.box(86, 150, 240, 150, "", fill=C["band"], stroke=C["ink2"]))
parts.append(F.note(102, 180, "heapUsed", "活对象", size=13))
parts.append(F.note(82, 322, "新生代·复制  老生代·增量标记压缩", size=11))
parts.append(F.note(82, 344, "大对象空间", size=11))
parts.append(F.note(344, 180, "heapTotal −", "heapUsed =", "已申请未占用", size=11))

# 右列：堆外
parts.append(F.box(470, 112, 284, 52, "", fill=C["card"], stroke=C["accent"]))
parts.append(F.note(486, 134, "external / arrayBuffers", "Buffer 堆外裸内存（第 7 章）", size=12))
parts.append(F.box(470, 178, 284, 52, "", fill=C["card"], stroke=C["line"]))
parts.append(F.note(486, 200, "libuv / C++ 结构", "句柄、解析器、请求上下文", size=12))
parts.append(F.box(470, 244, 284, 52, "", fill=C["card"], stroke=C["line"]))
parts.append(F.note(486, 266, "线程栈 · 代码", "线程池 / 平台线程 / JIT", size=12))
parts.append(F.box(470, 310, 284, 52, "", fill=C["card"], stroke=C["line"]))
parts.append(F.note(486, 332, "内核侧缓冲", "socket 收发队列（计入 rss）", size=12))

# 底部读法
parts.append(F.box(46, 422, 728, 40, "rss ⊃ heapTotal ⊃ heapUsed；external 在 rss 内、堆外 —— 堆快照干净 ≠ 没泄漏", fill=C["band"], tfill=C["label"], bold=True, fs=12.5))

F.build(OUT, 820, 480, *parts)
