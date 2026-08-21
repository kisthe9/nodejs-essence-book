"""图 6-2 重定向：shell 在 fork 与 exec 之间用 dup2 换牌。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-6-2.svg")
C = F.C

parts = [F.header(820, "重定向：程序登场前换掉它桌上的号码牌", "SHELL REDIRECT · DUP2")]

parts.append(F.stage(46, 92, 728, 46, 1, "shell fork 出子进程", "子进程继承整张 fd 表"))
parts.append(F.varrow(410, 138, 150))
parts.append(F.stage(46, 154, 728, 46, 2, "子进程 open(\"out.log\")", "得到当前最小空闲号 · 比如 fd 3"))
parts.append(F.varrow(410, 200, 212))
parts.append(F.stage(46, 216, 728, 60, 3, "dup2(3, 1)", "把 fd 1 的表项改指到 out.log 的 struct file", active=True, sub="随后关闭 fd 3 —— 1 号位从此姓 out.log"))
parts.append(F.varrow(410, 276, 288))
parts.append(F.stage(46, 292, 728, 60, 4, "exec(\"node\")", "新程序装入", sub="对 fd 表动过的手脚一无所知"))
parts.append(F.varrow(410, 352, 364))
parts.append(F.box(46, 368, 728, 52, "console.log(...) 照旧写 fd 1 → 字节实际落进 out.log", fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True, fs=13))

parts.append(F.note(46, 452, "重定向不是“修改输出”：程序只认 fd，指向谁由启动者决定", size=12.5))

F.build(OUT, 820, 476, *parts)
