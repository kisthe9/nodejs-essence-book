"""图 15-1 同步世界的调用栈：上下文就长在栈上。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-15-1.svg")
C = F.C

parts = [F.header(820, "同步世界：调用栈自带上下文", "CALL STACK AS CONTEXT")]

parts.append(F.zone(46, 76, 520, 280, "SYNC · 一条完整的栈"))
# 树状三层调用
parts.append(F.box(96, 116, 240, 42, "handle(req42)", stroke=C["ink2"], bold=True, fs=13))
parts.append(F.line(128, 158, 128, 202))
parts.append(F.line(128, 202, 176, 202))
parts.append(F.box(176, 182, 240, 42, "checkAuth()", stroke=C["ink2"], fs=12.5))
parts.append(F.line(208, 224, 208, 268))
parts.append(F.line(208, 268, 256, 268))
parts.append(F.box(256, 248, 240, 42, "log('ok')", stroke=C["ink2"], fs=12.5))

# 回溯箭头：沿栈向上
parts.append(F.path_arrow("M 520 268 V 142", accent=True))
parts.append(F.note(330, 310, "沿调用栈向上回溯，就知道", "“我在为 req42 工作”", accent=True, size=12))

# 右栏
parts.append(F.vrule(590, 84, 350))
parts.append(F.ksection(614, 100, "WHY IT WORKS", "栈帧层层相叠", [
    ("每个函数都记得是谁调的", "body"),
    ("任何深度可顺栈回溯", "body"),
    ("同步世界无需额外机制", "body"),
    ("但异步会把栈炸掉", "muted"),
    ("回调入场时原栈早已退栈", "muted"),
]))

parts.append(F.box(46, 380, 728, 40, "同步不需要任何额外机制——栈本身就是“来龙去脉”；问题从异步开始",
                   fill=C["band"], tfill=C["label"], bold=True, fs=12))

F.build(OUT, 820, 450, *parts)
