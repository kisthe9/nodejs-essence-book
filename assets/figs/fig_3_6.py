"""图 3-6 一个回调的一生 · 四站（四栏并列）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-3-6.svg")
C = F.C


def station(x, n, title, bound, d1, d2, accent=False):
    y = 140
    out = [
        f'<rect x="{x}" y="{y}" width="164" height="186" rx="4" fill="{C["card"]}" stroke="{C["line"]}" stroke-width="1.2"/>',
        F.badge(x + 14, y + 16, n, accent=accent),
        f'<text x="{x+42}" y="{y+31}" font-size="12.5" font-weight="700" fill="{C["label"]}">{title}</text>',
        f'<text x="{x+14}" y="{y+70}" font-size="11" font-weight="700" fill="{C["accent_deep"]}">{bound}</text>',
        f'<line x1="{x+14}" y1="{y+82}" x2="{x+58}" y2="{y+82}" stroke="{C["accent"]}" stroke-width="2"/>',
        f'<text x="{x+14}" y="{y+112}" font-size="11.5" fill="{C["body"]}">{d1}</text>',
        f'<text x="{x+14}" y="{y+134}" font-size="11.5" fill="{C["body"]}">{d2}</text>',
    ]
    return '\n'.join(out)


parts = [F.header(820, "一个回调的一生 · 四站", "A CALLBACK'S LIFE")]

parts.append(station(46, 1, "封装（本章）", "穿越语言边界", "JS 函数被封存为", "C++ 可持有的实体", accent=True))
parts.append(station(234, 2, "调度（第 4 章）", "穿越时间边界", "七个瓣膜决定", "它何时出闸"))
parts.append(station(422, 3, "喂数（第 6 章）", "穿越进程边界", "它的数据可能来自", "另一个进程的管道"))
parts.append(station(610, 4, "认出（第 15 章）", "穿越因果边界", "每次进场验护照，", "知道在为谁工作"))

# 站与站之间的推进
for x in (212, 400, 588):
    parts.append(F.arrow(x, 233, x + 18, 233))

F.build(OUT, 820, 420, *parts)
