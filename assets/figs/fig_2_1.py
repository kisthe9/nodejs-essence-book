"""图 2-1 V8 三层执行结构（Isolate / Context / HandleScope）· 嵌套 zone。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-2-1.svg")
C = F.C


def title(x, y, text, fs=14):
    return f'<text x="{x}" y="{y}" font-size="{fs}" fill="{C["ink"]}" font-weight="800">{text}</text>'


def bullet(x, y, text, fill=None, fs=12, bold=False):
    fill = fill or C["body"]
    wt = ' font-weight="700"' if bold else ''
    return f'<text x="{x}" y="{y}" font-size="{fs}" fill="{fill}"{wt}>{text}</text>'


parts = [F.header(820, "V8 的三层执行结构", "V8 RUNTIME STRUCTURE")]

# 第一层 · Isolate
parts.append(F.zone(46, 82, 728, 468, "ISOLATE · 隔离舱"))
parts.append(title(70, 140, "Isolate · 隔离舱"))
parts.append(bullet(70, 168, "· 一个独立的 V8 实例"))
parts.append(bullet(70, 192, "· 独立的堆内存、独立的垃圾回收器"))
parts.append(bullet(70, 216, "· 规则：同一时刻只允许一个线程进入", fill=C["accent_deep"], bold=True))

# 第二层 · Context
parts.append(F.zone(86, 240, 648, 286, "CONTEXT · 执行上下文"))
parts.append(title(110, 294, "Context · 执行上下文", fs=13.5))
parts.append(bullet(110, 322, "· 一套独立的全局对象与内建函数"))
parts.append(bullet(110, 346, "· 同一 Isolate 可有多个 Context"))

# 第三层 · HandleScope
parts.append(F.zone(126, 370, 568, 132, "HANDLE SCOPE · 句柄作用域"))
parts.append(title(150, 424, "HandleScope · 句柄作用域", fs=13))
parts.append(bullet(150, 452, "· C++ 侧引用 JS 对象的登记簿"))
parts.append(bullet(150, 476, "· 告诉 GC 哪些对象还不能回收"))

F.build(OUT, 820, 580, *parts)
