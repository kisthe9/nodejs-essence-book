"""图 12-4 善终流程：beforeExit 的挽留环 → exit 遗言 → 清理队列。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-12-4.svg")
C = F.C

parts = [F.header(820, "自然死亡：善终的三步", "GRACEFUL EXIT · BEFOREEXIT LOOP")]

# 主干
parts.append(F.box(210, 84, 220, 36, "事件循环空了", stroke=C["ink2"], bold=True))
parts.append(F.varrow(320, 122, 142))

parts.append(F.box(210, 146, 220, 42, "触发 process.on('beforeExit')", fs=12, stroke=C["ink2"]))
parts.append(F.varrow(320, 190, 268))

parts.append(F.box(210, 272, 220, 48, "回调安排了新异步任务？", fill=C["band"], stroke=C["ink2"], fs=12, bold=True))
parts.append(F.note(250, 340, "否", size=11.5))
parts.append(F.varrow(320, 322, 376))

parts.append(F.box(210, 380, 220, 42, "触发 process.on('exit')", fs=12, stroke=C["ink2"]))
parts.append(F.note(446, 400, "只能跑同步代码：循环已停摆", size=11))
parts.append(F.varrow(320, 424, 452))

parts.append(F.box(210, 456, 220, 42, "清理队列 · 进程终止", fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True, fs=12))
parts.append(F.note(446, 478, "第 11 章 Environment 的那条队列", size=11))

# 挽留环：是 → 回到循环 → 再次空了 → 再次 beforeExit
parts.append(F.path_arrow("M 432 296 H 560 V 167 H 436", accent=True))
parts.append(F.note(468, 288, "是", accent=True, size=11.5))
parts.append(F.box(560, 222, 190, 40, "回到事件循环继续跑", stroke=C["accent"], tfill=C["label"], fs=11.5))
parts.append(F.note(576, 152, "再次排空 ⇒ 再次触发", "beforeExit 可能触发多次", size=10.5))

# 旁路：process.exit
parts.append(F.note(46, 536, "旁路：process.exit() 跳过挽留直入 exit —— 缓冲区里的异步写随之丢失（拉闸）", size=11.5))

F.build(OUT, 820, 560, *parts)
