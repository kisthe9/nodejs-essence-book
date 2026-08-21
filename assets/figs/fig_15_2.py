"""图 15-2 asyncId 族谱树：每个异步资源的出生证明。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-15-2.svg")
C = F.C

parts = [F.header(820, "asyncId 族谱：每个异步操作的出生证明", "ASYNC GENEALOGY TREE")]

# 根：HTTP 请求回调
parts.append(F.box(70, 96, 320, 44, "HTTP 请求回调 · asyncId = 10", stroke=C["ink"], bold=True, fs=12.5))

# 主干竖线
parts.append(F.line(102, 140, 102, 404))

# 子节点 1：setTimeout
parts.append(F.line(102, 186, 168, 186))
parts.append(F.box(168, 166, 300, 40, "setTimeout · asyncId = 11", stroke=C["ink2"], fs=12))
parts.append(F.note(484, 190, "trigger = 10", size=11))

# 子节点 2：fs.readFile
parts.append(F.line(102, 252, 168, 252))
parts.append(F.box(168, 232, 300, 40, "fs.readFile · asyncId = 12", stroke=C["ink2"], fs=12))
parts.append(F.note(484, 256, "trigger = 10", size=11))

# 孙节点：setImmediate（挂在 readFile 下）
parts.append(F.line(200, 272, 200, 322))
parts.append(F.line(200, 322, 258, 322))
parts.append(F.box(258, 302, 330, 40, "setImmediate · asyncId = 13", stroke=C["ink2"], fs=12))
parts.append(F.note(604, 326, "trigger = 12", size=11))

# 子节点 3：省略
parts.append(F.line(102, 404, 168, 404))
parts.append(F.box(168, 388, 300, 32, "……（此后创建的每个异步资源）", stroke=C["line"], tfill=C["muted"], fs=11.5))

# 底部：沿 trigger 回溯 + 签发机关
parts.append(F.note(70, 448, "顺着 trigger 一路往上找，任何回调都能回答“我的祖先是谁”", accent=True, size=12))
parts.append(F.box(46, 462, 728, 40,
                   "asyncId = 我是谁 · triggerAsyncId = 谁创建了我 —— AsyncWrap 签发，CallbackScope 维护当前值",
                   fill=C["band"], tfill=C["label"], bold=True, fs=12))

F.build(OUT, 820, 524, *parts)
