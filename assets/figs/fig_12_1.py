"""图 12-1 启动装配线：node app.js 到事件循环的五站。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-12-1.svg")
C = F.C

parts = [F.header(820, "启动装配线：从 main 到事件循环", "BOOTSTRAP PIPELINE")]

parts.append(F.pill(270, 84, 180, "node app.js", h=30))
parts.append(F.varrow(270, 116, 132))

stages = [
    (136, 40, 1, "进程级初始化", "每进程一次 · 参数解析 / V8 平台 / libuv", False, None),
    (186, 40, 2, "创建三层容器", "Isolate → Environment → Realm 与 Context", False, None),
    (236, 52, 3, "执行内部引导脚本", "primordials → Binding → process", True, "③c：process 诞生于此 · 挂上全局"),
    (300, 40, 4, "加载用户主模块", "你的 app.js · 经 CJS / ESM 加载器", False, None),
    (350, 40, 5, "进入事件循环", "第 4 章的心脏开始跳动", False, None),
]
for y, h, num, label, desc, active, sub in stages:
    parts.append(F.stage(70, y, 400, h, num, label, desc, active=active, sub=sub))
for y1, y2 in [(176, 183), (226, 233), (288, 297), (340, 347)]:
    parts.append(F.varrow(270, y1, y2))

# 右栏：引导脚本的严格顺序
parts.append(F.vrule(492, 84, 396))
parts.append(F.ksection(516, 96, "BOOTSTRAP ORDER", "引导脚本 · 严格顺序", [
    ("a. 加固内建 primordials", "body"),
    ("b. 搭 Binding 通道（第 3 章）", "body"),
    ("c. 创建 process 对象 · 挂全局", "body"),
    ("d. 按启动方式补配置", "body"),
    ("主脚本？REPL？Worker？", "muted"),
]))
parts.append(F.ksection(516, 292, "SNAPSHOT", "快照 · 为什么这么快", [
    ("构建期执行引导 · 序列化堆", "body"),
    ("启动期反序列化 · 跳过执行", "body"),
    ("空间（二进制体积）换时间", "muted"),
]))

parts.append(F.note(70, 424, "几十毫秒内完成全部装配——一半功劳归快照", size=12))

F.build(OUT, 820, 450, *parts)
