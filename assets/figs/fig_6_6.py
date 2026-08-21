"""图 6-6 回调接力：一次 child.send 的完整旅程（三泳道）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-6-6.svg")
C = F.C

W, H = 820, 620

parts = [F.header(W, "回调接力：IPC 在暗线上的位置", "SEND · PIPE · EPOLL · EMIT")]

# 泳道头
for x, t in [(58, "进程 A"), (300, "内核"), (558, "进程 B")]:
    parts.append(F.box(x, 80, 200, 30, t, stroke=C["ink2"], bold=True, fs=12.5))
parts.append(F.lane_divider(278, 118, 560))
parts.append(F.lane_divider(536, 118, 560))

# A：send
parts.append(F.box(58, 136, 200, 42, "send(msg) · JSON 序列化", fs=11.5))
parts.append(F.badge(246, 126, 1))

# A → 内核：write
parts.append(F.path_arrow("M 158 178 V 226 H 296"))
parts.append(F.note(170, 202, "write(pipe-fd)", size=11))
parts.append(F.note(170, 218, "（5.1 的多态分发）", size=10.5))

# 内核：缓冲区
parts.append(F.box(300, 250, 200, 46, "", stroke=C["accent"]))
parts.append(f'<text x="400" y="270" text-anchor="middle" font-size="12" font-weight="700" fill="{C["label"]}">64KB 环形缓冲</text>')
parts.append(f'<text x="400" y="288" text-anchor="middle" font-size="10.5" fill="{C["muted"]}">字节先进这里</text>')
parts.append(F.badge(488, 240, 2))

# 内核就绪 → B 的 poll
parts.append(F.note(300, 330, "pipe 读端就绪", size=11))
parts.append(F.badge(392, 316, 3))
parts.append(F.arrow(554, 356, 504, 356))
parts.append(F.note(556, 348, "epoll_wait", size=11.5))
parts.append(F.note(556, 366, "（B 的 poll 瓣膜）", size=10.5))

# 内核 → B：返回就绪 fd
parts.append(F.arrow(504, 402, 554, 402))
parts.append(F.note(408, 396, "返回就绪 fd", size=11.5))
parts.append(F.badge(478, 388, 4))

# B：read 与切分
parts.append(F.box(558, 424, 200, 40, "read() 取出字节", fs=11.5))
parts.append(F.badge(746, 414, 5))
parts.append(F.varrow(658, 464, 480))
parts.append(F.box(558, 484, 200, 40, "切分消息边界", fs=11.5))
parts.append(F.badge(746, 474, 6))
parts.append(F.varrow(658, 524, 540))

# B：MakeCallback → emit → 回调
parts.append(F.box(558, 544, 200, 42, "MakeCallback · emit('message')", fs=11))
parts.append(F.badge(746, 534, 7))

parts.append(F.note(46, 596, "进程 B 里发生的一切 = 第 4 章瓣膜的原样重演：A 的 write 是上一棒，B 的回调是下一棒", size=12, accent=True))

F.build(OUT, W, H, *parts)
