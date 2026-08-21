"""图 3-4 BaseObject 继承链：统一各种资源（纵向递进）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "figlib"))
import figlib as F

OUT = os.path.join(os.path.dirname(__file__), "..", "fig-3-4.svg")
C = F.C


def text(x, y, s, fs=12, fill=None, bold=False):
    fill = fill or C["body"]
    wt = ' font-weight="700"' if bold else ''
    return f'<text x="{x}" y="{y}" font-size="{fs}" fill="{fill}"{wt}>{s}</text>'


parts = [F.header(820, "BaseObject 继承链 · 统一各种资源", "INHERITANCE CHAIN")]

# 四级递进（逐级缩进，伏笔：TCPWrap 与 PipeWrap 是亲兄弟）
rows = [
    (90, "BaseObject", "JS/C++ 对象绑定的地基"),
    (150, "AsyncWrap", "加上异步追踪身份证（asyncId，第 9 章再见）"),
    (210, "HandleWrap", "加上 libuv 句柄的生命周期管理"),
    (270, "各种资源包装", "TCPWrap / PipeWrap / TTYWrap / ..."),
]
ys = [110, 196, 282, 368]
BW, BH = 220, 48

for (x, name, desc), y in zip(rows, ys):
    fill = C["ink"] if name == "BaseObject" else C["card"]
    tf = "#ffffff" if name == "BaseObject" else C["label"]
    parts.append(F.box(x, y, BW, BH, name, fill=fill, stroke=C["ink2"] if name == "BaseObject" else C["line"],
                       tfill=tf, bold=True, fs=13))
    parts.append(text(x + BW + 26, y + BH / 2 + 4.5, "—— " + desc, fs=12, fill=C["body"]))

# └─ 连接
for i in range(3):
    x1, y1 = rows[i][0], ys[i]
    x2, y2 = rows[i + 1][0], ys[i + 1]
    parts.append(F.path_arrow(f"M {x1 + 40} {y1 + BH} V {(y1 + BH + y2) / 2} H {x2 + 40} V {y2 - 4}"))

F.build(OUT, 820, 460, *parts)
