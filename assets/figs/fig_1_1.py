"""图 1-1 C10K 的两种答案：线程模型 vs 事件模型。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-1-1.svg")
C = F.C

parts = [F.header(820, "C10K 的两种答案", "THREADS VS EVENT LOOP")]

# 左：线程模型
parts.append(F.zone(46, 76, 352, 310, "线程模型 · 每连接一线程"))
for i, x in enumerate([66, 178, 290], 1):
    parts.append(F.box(x, 112, 96, 34, f"线程 {i}", stroke=C["ink2"], bold=True))
    parts.append(F.arrow(x + 48, 146, x + 48, 154))
    parts.append(F.box(x, 156, 96, 34, "read() 阻塞", fill=C["band"], tfill=C["muted"]))
    parts.append(F.arrow(x + 48, 190, x + 48, 198))
    parts.append(F.box(x, 200, 96, 34, "等网卡", fill=C["band"], tfill=C["muted"]))
parts.append(F.note(66, 262, "× 10 000 份", size=13))
parts.append(F.note(66, 290, "每线程 ≈ 1MB 栈内存", "上下文切换随连接数线性增长", size=12))
parts.append(F.note(66, 336, "10 000 连接 ⇒ 仅栈 ≥ 5GB", size=12.5))

# 右：事件模型
parts.append(F.zone(422, 76, 352, 310, "事件模型 · 一个循环全部连接"))
for i in range(8):
    x = 442 + i * 40
    parts.append(F.box(x, 112, 30, 24, "conn", fs=10, tfill=C["muted"]))
    parts.append(F.line(x + 15, 136, x + 15, 168))
parts.append(F.line(457, 168, 737, 168))
parts.append(F.arrow(597, 168, 597, 204))
parts.append(F.box(442, 208, 312, 44, "事件循环 · 单线程", fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True, fs=13))
parts.append(F.arrow(597, 252, 597, 260))
parts.append(F.box(442, 262, 312, 34, "只处理就绪的连接 · 不等待", tfill=C["body"]))
parts.append(F.note(442, 322, "空闲连接不占线程", size=12.5))
parts.append(F.note(442, 344, "只占一个 fd + 一份内核结构", size=11.5))

# 底部对照
parts.append(F.box(46, 402, 352, 40, "线程模型 · 5000 连接 ⇒ 栈 ≥ 5GB", fill=C["band"], tfill=C["label"], bold=True))
parts.append(F.box(422, 402, 352, 40, "事件模型 · 5000 连接 ⇒ 全进程 74MB", fill=C["accent"], stroke=C["accent"], tfill="#ffffff", bold=True))

F.build(OUT, 820, 470, *parts)
