"""图 10-1 一个 HTTP 请求 · 零件合练（泳道序列 + 章节徽章）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-10-1.svg")
C = F.C

parts = [F.header(820, "一个 HTTP 请求 · 零件合练", "ONE REQUEST · ALL MECHANISMS")]

# 泳道头
for x, t in [(50, "内核"), (232, "libuv · C++"), (414, "JS 运行时"), (596, "你的代码")]:
    parts.append(F.box(x, 76, 174, 30, t, stroke=C["ink2"], bold=True, fs=12.5))
for x in (228, 410, 592):
    parts.append(F.lane_divider(x, 112, 556))

# 步骤
parts.append(F.box(57, 140, 160, 40, "包到达 · epoll 举手", fs=11.5))
parts.append(F.badge(57 + 160 - 12, 130, 5))

parts.append(F.arrow(217, 220, 235, 220))
parts.append(F.box(239, 200, 160, 40, "read() 入 Buffer", fs=11.5))
parts.append(F.badge(239 + 160 - 12, 190, 7))

parts.append(F.box(239, 260, 160, 40, "llhttp · 同步解析", fill=C["ink"], stroke=C["ink"], tfill="#ffffff", fs=11.5, bold=True))
parts.append(F.badge(239 + 160 - 12, 250, 10))

parts.append(F.arrow(399, 340, 417, 340))
parts.append(F.box(421, 320, 160, 40, "emit('request')", fs=11.5))
parts.append(F.badge(421 + 160 - 12, 310, 9))

parts.append(F.arrow(581, 400, 599, 400))
parts.append(F.box(603, 380, 160, 40, "回调跑 · res.write", fs=11.5))
parts.append(F.badge(603 + 160 - 12, 370, 8))

parts.append(F.arrow(603, 460, 221, 460))
parts.append(F.note(300, 452, "write() · 同一个 fd，同一个系统调用", size=11.5))
parts.append(F.badge(225, 470, 6))

parts.append(F.box(57, 500, 160, 40, "fd 不挂 · 等下一请求", fs=11.5))
parts.append(F.badge(57 + 160 - 12, 490, 4))

# 图例
parts.append(F.badge(46, 576, 10))
parts.append(F.note(74, 591, "徽章数字 = 该机制的讲解章节", size=11.5))

F.build(OUT, 820, 620, *parts)
