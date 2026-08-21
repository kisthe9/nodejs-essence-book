"""图 12-2 process 三步长成：空壳 → 装配 → 挂全局。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-12-2.svg")
C = F.C

parts = [F.header(820, "process 的长成：空壳 · 装配 · 挂全局", "PROCESS · THREE GROWTH STEPS")]

# ① 空壳
parts.append(F.stage(70, 84, 460, 44, 1, "C++ 立空壳", "近白板 JS 对象 · 登记为 process_object()"))
parts.append(F.note(70, 148, "src/node.cc 建环境时创建 —— 投影的锚点", size=11))
parts.append(F.varrow(300, 156, 172))

# ② 装配
parts.append(F.zone(70, 176, 460, 250, "② 引导脚本逐件装配 · pre_execution.js"))
items = [
    ("并入 C++ 方法", "pid / kill / exit…… 经 internalBinding('process_methods') 投影"),
    ("切换原型", "换成 EventEmitter.prototype —— process.on('exit') 由此而来"),
    ("挂数据", "argv 是解析成品；env 是环境表实时代理，读写直达 getenv/setenv"),
    ("stdio 惰性 getter", "首碰 process.stdout 才按 fd 1 真身定同步/异步写（第 6 章）"),
]
y = 208
for i, (lab, desc) in enumerate(items, 1):
    parts.append(F.badge(90, y, i, accent=False))
    parts.append(F.note(122, y + 15, lab, size=12.5))
    parts.append(F.note(122, y + 33, desc, size=10.5))
    y += 54

parts.append(F.varrow(300, 428, 446))

# ③ 挂全局
parts.append(F.stage(70, 450, 460, 44, 3, "挂全局", "globalThis.process 就位 · 用户代码可见", active=True))
parts.append(F.note(70, 516, "身上几乎每样东西都转发给 C++ 侧 Environment —— process 是投影不是本体", size=11.5))

# 右栏：投影的含义
parts.append(F.vrule(560, 84, 520))
parts.append(F.ksection(584, 100, "PROJECTION", "为什么叫投影", [
    ("process.env → C++ 环境表", "body"),
    ("process.exit → 环境的退出流程", "body"),
    ("process.memoryUsage → Binding", "body"),
    ("面貌随启动方式微调", "muted"),
    ("主脚本 / REPL / Worker", "muted"),
    ("装配清单各不相同", "muted"),
]))

F.build(OUT, 820, 560, *parts)
