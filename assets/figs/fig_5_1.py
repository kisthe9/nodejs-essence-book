"""图 5-1 两条 I/O 之路：网络 epoll vs 磁盘线程池（双 zone 分叉 + 汇合）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-5-1.svg")
C = F.C


def ctext(x, y, text, size=11.5, fill=None, weight=None):
    fill = fill or C["muted"]
    wt = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="{fill}"{wt}>{text}</text>'


parts = [F.header(820, "两条 I/O 之路", "TWO ROADS · ONE ASYNC")]

# 顶部分叉
parts.append(F.pill(410, 82, 240, "Node.js 的异步 I/O", h=36))
parts.append(F.path_arrow("M 410 118 V 138 H 222 V 156"))
parts.append(F.path_arrow("M 410 118 V 138 H 598 V 156"))

# 左 zone：网络路
parts.append(F.zone(46, 160, 352, 236, "网络路 · 真异步"))
parts.append(F.box(86, 196, 272, 38, "socket / pipe", stroke=C["ink2"], bold=True, fs=12.5))
parts.append(F.varrow(222, 234, 256))
parts.append(F.box(86, 260, 272, 38, "epoll 事件通知", fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True))
parts.append(F.note(86, 326, "主线程从不为它阻塞", accent=True, size=12))
parts.append(F.note(86, 348, "就绪与否是真实状态 · 内核可通知", size=11))

# 右 zone：文件路
parts.append(F.zone(422, 160, 352, 236, "文件路 · 模拟异步"))
parts.append(F.box(462, 196, 272, 38, "文件读写 · DNS 解析 · 部分加密", stroke=C["ink2"], bold=True, fs=11.5))
parts.append(F.varrow(598, 234, 256))
parts.append(F.box(462, 260, 272, 38, "libuv 线程池", fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True))
parts.append(F.note(462, 326, "默认 4 个工人线程替主线程去阻塞", accent=True, size=12))
parts.append(F.note(462, 348, "文件永远就绪 · 事件通知对它失效", size=11))

# 底部汇合
parts.append(F.path_arrow("M 222 396 V 426 H 326 V 448"))
parts.append(F.path_arrow("M 598 396 V 426 H 494 V 448"))
parts.append(F.box(250, 452, 320, 44, "同一个 uv_run 循环 · 同一种回调风格", bold=True, fs=12.5))
parts.append(ctext(410, 526, "底下，是两套完全不同的机制", 12, C["body"]))

F.build(OUT, 820, 550, *parts)
