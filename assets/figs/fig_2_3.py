"""图 2-3 GC 暂停 · 请求时间轴（横向 box 序列 + note）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-2-3.svg")
C = F.C


def ctext(x, y, text, fs=12, fill=None, bold=False):
    fill = fill or C["body"]
    wt = ' font-weight="700"' if bold else ''
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{fs}" fill="{fill}"{wt}>{text}</text>'


parts = [F.header(820, "GC 暂停 · 请求时间轴", "GC STOP-THE-WORLD")]

# 时间轴
parts.append(f'<text x="60" y="150" font-size="12" fill="{C["muted"]}" letter-spacing="2">时间轴</text>')
parts.append(F.arrow(60, 184, 748, 184))

# 轴上的处理序列（GC 暂停为唯一高亮）
parts.append(F.box(96, 162, 130, 44, "处理请求 A", fs=12))
parts.append(F.box(234, 162, 130, 44, "处理请求 B", fs=12))
parts.append(F.box(372, 162, 190, 44, "GC 暂停 80ms",
                   fill=C["accent"], stroke=C["accent"], tfill="#ffffff", bold=True, fs=12.5))
parts.append(F.box(570, 162, 130, 44, "处理请求 C", fs=12))

# 警示三角 + 注解
parts.append(f'<path d="M 467 218 L 459 232 L 475 232 Z" fill="{C["accent_deep"]}"/>')
parts.append(ctext(467, 264, "所有排队中的请求集体多等 80ms", fs=12.5, fill=C["accent_deep"], bold=True))
parts.append(ctext(467, 290, "（p99 延迟毛刺的常见来源）", fs=11.5, fill=C["muted"]))

F.build(OUT, 820, 420, *parts)
