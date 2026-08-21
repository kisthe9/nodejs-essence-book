"""图 8-3 刹车一路踩到底层：从 JS 到 TCP 窗口。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-8-3.svg")
C = F.C

W, H = 820, 550

stages = [
    ("JS", "pause()", "上游停止读取"),
    ("C++", "uv_read_stop", "停止 libuv 的读取"),
    ("libuv", "把 fd 从 epoll 关注列表移除", "不再收“可读”通知"),
    ("内核", "socket 接收缓冲区渐满", "无人来取"),
    ("TCP", "通告窗口缩小", "发送端减速 / 停发"),
    ("对端机器", "感知到压力", "它的写也开始返回 false…"),
]

parts = [F.header(W, "刹车一路踩到底层", "PAUSE → EPOLL → TCP WINDOW")]

centers = []
for i, (layer, label, desc) in enumerate(stages):
    x = 46 + i * 16
    w = 728 - i * 16
    y = 96 + i * 64
    parts.append(F.stage(x, y, w, 44, i + 1, f"{layer} · {label}", desc, active=(i == 5)))
    centers.append((x + w / 2, y))

for i in range(5):
    cx1, y1 = centers[i]
    cx2, y2 = centers[i + 1]
    yb = y1 + 44
    parts.append(F.path_arrow(f"M {cx1} {yb} V {yb+10} H {cx2} V {y2-2}"))

parts.append(F.note(46, 500, "背压穿透 JS · C++ · 内核，一路传到网线对面的发送端", size=12.5, accent=True))
parts.append(F.note(46, 524, "整条流水线以最慢一环的速度运转 —— 不是靠更大的缓冲", size=12))

F.build(OUT, W, H, *parts)
