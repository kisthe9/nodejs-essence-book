"""图 4-1 事件循环：uv_run 的一圈（线性流程类样张/首张生产图）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-4-1.svg")

stages = [
    (112, 40, 1, "timers", "到期的定时器"),
    (162, 40, 2, "pending", "推迟的系统错误"),
    (212, 40, 3, "idle / prepare", "内部插桩"),
    (262, 48, 4, "poll", "收割就绪事件", True, "心脏主腔 · 空闲时阻塞于此"),
    (320, 40, 5, "check", "setImmediate"),
    (370, 40, 6, "close", "关闭类回调"),
]

parts = [F.header(820, "事件循环：uv_run 的一圈", "EVENT LOOP · ONE TICK")]
parts.append(F.zone(46, 76, 352, 362, "ONE TICK · 一圈"))

for s in stages:
    y, h, num, label, desc = s[:5]
    active = len(s) > 5 and s[5]
    sub = s[6] if len(s) > 6 else None
    parts.append(F.stage(66, y, 312, h, num, label, desc, active=active, sub=sub))

for y1, y2 in [(152, 159), (202, 209), (252, 259), (310, 317), (360, 367)]:
    parts.append(F.varrow(222, y1, y2))

parts.append(F.path_arrow("M 378 390 H 448 V 132 H 382", accent=True))
parts.append(F.note(458, 256, "还有活", "转下一圈", accent=True))

parts.append(F.path_arrow("M 222 410 V 448"))
parts.append(F.note(237, 434, "无事可做", size=11.5))
parts.append(F.pill(222, 452, 170, "进程自然退出"))

parts.append(F.vrule(512, 80, 438))
parts.append(F.ksection(536, 102, "BETWEEN PHASES", "阶段之间", [
    ("排空 nextTick 队列", "body"),
    ("排空 Promise 微任务", "body"),
    ("递归微任务会饿死循环", "muted"),
    ("过闸动作：MakeCallback", "body"),
]))
parts.append(F.ksection(536, 296, "LIVENESS", "存活判据", [
    ("每圈结束清点活跃句柄", "body"),
    ("listen() 让进程不死", "muted"),
]))

F.build(OUT, 820, 500, *parts)
