"""图 3-5 MakeCallback 的三段动作（回程通道 · 纵向 stage）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-3-5.svg")
C = F.C

parts = [F.header(820, "MakeCallback 的三段动作", "MAKECALLBACK · RETURN PATH")]

# 入口链：libuv 事件 → C++ 回调 → MakeCallback
parts.append(F.box(90, 88, 150, 36, "libuv 事件", bold=True))
parts.append(F.arrow(240, 106, 286, 106))
parts.append(F.box(290, 88, 150, 36, "C++ 回调", bold=True))
parts.append(F.arrow(440, 106, 486, 106))
parts.append(F.box(490, 88, 180, 36, "MakeCallback", fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True))
parts.append(F.path_arrow("M 580 124 V 148 H 410 V 164"))

# 三段动作
X, W, H = 90, 640, 62
ys = [168, 252, 336]
parts.append(F.stage(X, ys[0], W, H, "①", "进入 CallbackScope", "把“当前异步上下文”切换为该回调对应的值",
                     sub="——第 15 章的护照查验，就在这一步发生"))
parts.append(F.stage(X, ys[1], W, H, "②", "在 TryCatch 兜底中调用 JS 函数", "异常不会炸穿 C++ 栈",
                     sub="异常被兜住，回调返回后转投 process 的 'uncaughtException'（第 9 章快速失败）"))
parts.append(F.stage(X, ys[2], W, H, "③", "回调返回后，排空 nextTick / 微任务队列", "第 4 章的“阶段间隙”",
                     sub="——然后才把控制权交还事件循环"))

parts.append(F.varrow(X + W / 2, ys[0] + H + 2, ys[1] - 2))
parts.append(F.varrow(X + W / 2, ys[1] + H + 2, ys[2] - 2))

F.build(OUT, 820, 440, *parts)
