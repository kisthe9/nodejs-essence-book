"""图 9-2 'error' 铁律：没监听器就 throw，就崩溃。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-9-2.svg")
C = F.C

W, H = 820, 450

parts = [F.header(W, "'error'：唯一的特殊事件", "ERROR RULE · FAIL FAST")]

parts.append(F.box(290, 96, 240, 48, "emit('error', err)", fill=C["ink"], stroke=C["ink"], tfill="#ffffff", bold=True, fs=13))

# 分支
parts.append(F.arrow(350, 144, 210, 190))
parts.append(F.arrow(470, 144, 610, 190))

# 左：有监听器
parts.append(F.box(80, 194, 260, 56, "", stroke=C["line"]))
parts.append(f'<text x="96" y="218" font-size="13" font-weight="700" fill="{C["label"]}">有监听器</text>')
parts.append(f'<text x="96" y="238" font-size="11.5" fill="{C["muted"]}">正常同步分发 · 跟别的事件一样</text>')

# 右：没监听器
parts.append(F.box(480, 194, 260, 56, "", stroke=C["accent"]))
parts.append(f'<text x="496" y="218" font-size="13" font-weight="700" fill="{C["accent_deep"]}">没监听器</text>')
parts.append(f'<text x="496" y="238" font-size="11.5" fill="{C["body"]}">直接 throw err</text>')

parts.append(F.varrow(610, 250, 284))
parts.append(F.box(480, 288, 260, 44, "没有 try/catch 接住", fs=12))
parts.append(F.varrow(610, 332, 366))
parts.append(F.box(480, 370, 260, 48, "进程崩溃退出", fill=C["accent"], stroke=C["accent"], tfill="#ffffff", bold=True, fs=13))

# 左侧注解
parts.append(F.note(80, 300, "快速失败设计：", size=12.5))
parts.append(F.note(80, 324, "要么显式处理，要么进程死给你看", size=12))
parts.append(F.note(80, 372, "铁律：长期存活的 emitter 必挂 'error' 监听", accent=True, size=12))
parts.append(F.note(80, 396, "uncaughtException 是最后底线，不是免死金牌", size=11.5))

F.build(OUT, W, H, *parts)
