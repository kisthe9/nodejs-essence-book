"""图 6-7 EMFILE：号码牌用完时的雪崩。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-6-7.svg")
C = F.C

W, H = 820, 470

parts = [F.header(W, "EMFILE：号码牌用完的雪崩", "FD EXHAUSTION · CASCADE")]

parts.append(F.stage(46, 92, 728, 48, 1, "忘记 close（文件）/ 连接未正确关闭", "CLOSE-WAIT 堆积 —— 泄漏持续积累"))
parts.append(F.varrow(410, 140, 154))
parts.append(F.stage(46, 158, 728, 48, 2, "fd 表渐满 → 达到上限", "ulimit -n · 常见默认 1024"))
parts.append(F.varrow(410, 206, 220))
parts.append(F.stage(46, 224, 728, 48, 3, "accept() 失败：EMFILE", "too many open files", active=True))
parts.append(F.varrow(410, 272, 286))
parts.append(F.stage(46, 290, 728, 60, 4, "新连接全部被拒", "打开任何文件也失败 —— 连日志都写不了", active=True))

parts.append(F.note(46, 392, "排查三板斧", size=12.5))
parts.append(F.note(46, 416, "lsof -p PID 看打开了什么 · ss -s 看 socket 状态分布 · CLOSE-WAIT 堆积 ≈ 对端关了我方忘了 close", size=12))
parts.append(F.note(46, 442, "泄漏的资源类型，直接写在 lsof 的 TYPE 列上", size=11.5, accent=True))

F.build(OUT, W, H, *parts)
