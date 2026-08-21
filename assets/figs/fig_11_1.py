"""图 11-1 三层容器嵌套：Isolate ⊃ Environment ⊃ Realm。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-11-1.svg")
C = F.C

parts = [F.header(820, "三层容器：一个 Node.js 实例的嵌套结构", "ISOLATE ⊃ ENVIRONMENT ⊃ REALM")]

# 外层：Isolate
parts.append(F.zone(46, 76, 452, 280, "V8 Isolate · 独立堆 · 独立 GC · 单线程"))
# 中层：Environment
parts.append(F.box(64, 146, 416, 86, "", fill=C["card"], stroke=C["ink2"]))
parts.append(F.note(80, 168, "Environment（C++ 类）· “一个 Node.js 实例”的真身", size=12.5))
parts.append(F.note(80, 190, "持有：事件循环 uv_loop_t · 清理队列 · Inspector · 权限控制", size=11))
parts.append(F.note(80, 220, "第 4 章的心脏与退出时的按序销毁，都住在这里", size=10.5))
# 内层：Realm
parts.append(F.box(82, 250, 380, 78, "", fill=C["band"], stroke=C["ink2"]))
parts.append(F.note(98, 272, "Realm · 绑定一个 V8 Context 的执行域", size=12.5))
parts.append(F.note(98, 294, "process 对象住在这里 · 内置模块缓存住在这里", size=11))

# 右栏：真身要点
parts.append(F.vrule(516, 80, 404))
parts.append(F.ksection(540, 96, "THE REAL SELF", "Environment 才是真身", [
    ("事件循环 uv_loop_t（第 4 章）", "body"),
    ("清理队列 · 退出时按序销毁", "body"),
    ("Inspector / 权限等子系统", "muted"),
    ("Realm = Context + process", "body"),
    ("        + 模块缓存", "muted"),
    ("Worker = 线程 + Isolate", "body"),
    ("        + Environment（第 14 章）", "muted"),
]))

# 底部一行收束
parts.append(F.box(46, 380, 728, 38,
                   "Isolate = 堆与 GC 的边界 · Environment = 实例实体 · Realm = 全局环境与 process",
                   fill=C["band"], tfill=C["label"], bold=True, fs=12))

F.build(OUT, 820, 440, *parts)
